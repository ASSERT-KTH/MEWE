import time
from common.common import *
from threading import Thread
from subprocess import Popen, PIPE, check_output, STDOUT
import sys
import os
import re
import matplotlib.pyplot as plt
from multiprocessing.pool import ThreadPool
import datetime
import numpy as np
from scipy import stats
import os


import urllib3
urllib3.disable_warnings()

pool = ThreadPool(processes=1)


class UserSpaceSniffer(object):

    def wrap_function(self, fn, *args, **kwargs):
        t0 = time.time()
        r = fn(*args, **kwargs)

        return r, time.time() - t0

class WireSharkSniffer(object):

    def __init__(self, filtered_ports=[80, 443],
    src_filter=[],
    dst_filter=[], timeout=0):
        self.filtered_ports = filtered_ports
        self.src_filter = src_filter
        self.dst_filter = dst_filter
        self.timeout=timeout

        #print(f"Timeout {timeout}")

        #self.event_parser = re.compile(r'^(?P<id>\d+) +(?P<date>\d+\.\d+) (?P<src_ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) → (?P<dst_ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (?P<protocol>\w+) (?P<process>\d+) (?P<src_port>\d+) → (?P<dst_port>\d+) (?P<actions>\[( ?\w+,?)+\])(?P<arguments>( ?\w+=\d+)+)')

    def check_and_filter_events_order(self, events):

        interactions = []
        buffer = []
        for event in events:
            #print(event)
            layers = event["_source"]["layers"]
            ip_layer = layers["ip"]
            if "tcp" in layers:
                tcp_layer = layers["tcp"]

                src_port = tcp_layer["tcp.srcport"]
                dst_port = tcp_layer["tcp.dstport"]

                if "tcp.options_tree" in tcp_layer:
                    tcp_options = tcp_layer["tcp.options_tree"]

                    tsval=tcp_options["tcp.options.timestamp_tree"]["tcp.options.timestamp.tsval"]
                    tsecr=tcp_options["tcp.options.timestamp_tree"]["tcp.options.timestamp.tsecr"]

                    if tsecr == "0": # start of a new communication
                        if len(buffer) > 0:
                            interactions.append(buffer)
                        #print(buffer)
                        buffer = [event]
                    else:
                        buffer.append(event)

        if len(buffer) > 0:
            first = buffer[0]

            if first["_source"]["layers"]["tcp"]["tcp.options_tree"]["tcp.options.timestamp_tree"]["tcp.options.timestamp.tsecr"] == "0":
                interactions.append(buffer)


        return interactions

    def get_rtts_from_tcp(self, interactions, src_ip, discard_first_n=0):
        result = []
        slopes = []
        for interaction in interactions:
            first = 0
            first_frame = 0
            sframe = 0
            s = 0

            deltas_tcp = []
            deltas_frame = []

            for event in interaction[discard_first_n:]: # Patch since for some reason the delay between requests is added to the interaction
                ip_layer = event["_source"]["layers"]["ip"]
                frame_layer = event["_source"]["layers"]["frame"]

                if ip_layer["ip.src"] == src_ip:
                    tcp_layer = event["_source"]["layers"]["tcp"]

                    if first_frame == 0:
                        first_frame = float(frame_layer["frame.time_epoch"])
                    else:
                        frame_delta = float(frame_layer["frame.time_epoch"]) - first_frame
                        sframe += frame_delta 
                        deltas_frame.append(frame_delta)
                        first_frame = float(frame_layer["frame.time_epoch"])

                    sframe = float(frame_layer["frame.time_epoch"]) - first_frame
                    if "tcp.options_tree" in tcp_layer:
                        tsval = tcp_layer["tcp.options_tree"]["tcp.options.timestamp_tree"]["tcp.options.timestamp.tsval"]
                        
                        if first == 0:
                            first += float(tsval)
                        else:
                            #print(tsval, float(tsval) - first)
                            tcp_delta = float(tsval) - first
                            s += tcp_delta
                            deltas_tcp.append(tcp_delta)
                            first = float(tsval)
            #doing linear regression

            if len(deltas_frame) != len(deltas_tcp):
                print("WARNING delta collections are different in size")
                raise Exception("Invalid deltas")

            if len(deltas_tcp) > 0:
                slope, intercept, r_value, p_value, std_err = stats.linregress(deltas_frame, deltas_tcp)

                pck_stats = dict(slope=slope, intercept=intercept, r_value=r_value, p_value =p_value, std_err=std_err, 
                samples_frame=deltas_frame, samples_tcp=deltas_tcp)

                #print(f"Slope {slope}, intercept: {intercept:.2f}")
                result.append(s)
                slopes.append(pck_stats)
            #print(s)
        #print(result)

        # linear regression to get slope

        return result, slopes

    def get_linear_regression(self, interactions, report_outliers=False):
        #TODO
        pass

    def project_package_info(self, package):
        
        result = dict()
        #print(json.dumps(package, indent=4))



        tcp_layer = package["_source"]["layers"]["tcp"]
        frame_layer = package["_source"]["layers"]["frame"]

        result["frame"] = dict(time_epoch=frame_layer["frame.time_epoch"], time=frame_layer["frame.time"])
        result["ip"] = package["_source"]["layers"]["ip"] # Full ip layer

        if "tcp.options_tree" in tcp_layer and "tcp.options.timestamp_tree" in tcp_layer["tcp.options_tree"]:
            result["tcp"] = dict(timestamp=tcp_layer["tcp.options_tree"]["tcp.options.timestamp_tree"])

        return result
    def get_rtts_from_frame(self, interactions):
        result = []
        for interaction in interactions:
            #print(f"Events {len(interaction)}")
            first = 0
            s = 0
            for event in interaction: # Discard last package
                tcp_layer = event["_source"]["layers"]["tcp"]
                frame_layer = event["_source"]["layers"]["frame"]
                if first == 0:
                    first += float(frame_layer["frame.time_epoch"])
                if first < 0: # discard x first packages
                    first += 1

                s = float(frame_layer["frame.time_epoch"]) - first
                #print(json.dumps(tcp_layer, indent=4))

                #if "tcp.analysis" in tcp_layer:
                  #  s += float(tcp_layer["tcp.analysis"][])
            #print(s)
            result.append(s)
        return result

    def stop_and_collect(self, src, dst):
        print("Stopping tshark collection")
        #print(r)
        self.process.terminate()
        std, err = self.process.communicate()
        #print(err.decode(), std.decode())

        data = json.loads(std)
        events = []
        for p in data:
            # Filtering IP host and dst
            
            layers = p["_source"]["layers"]
            #frame_time_stamp = layers["frame"]["frame.time"]
            #if "tcp" not in layers: ## If no tcp layer is present, then packages are filtered
            #    continue 
            if "ip" in layers:
                ip_layer = layers['ip']
                src_ip = ip_layer["ip.src"]
                dst_ip = ip_layer["ip.dst"]

                if (src_ip == src and dst_ip == dst) or (src_ip == dst and dst_ip == src):
                    events.append(p)
                
        print(f"{len(events)} collected packages")
        return events

    def capture_packages(self, src, dst):
        possible_paths = []
        process_name = "tshark"
        os_path = os.getenv(
            "PATH",
            "/usr/bin:/usr/sbin:/usr/lib/tshark:/usr/local/bin"
        )
        for path in os_path.split(":"):
            possible_paths.append(os.path.join(path, process_name))

        path = None
        for p in possible_paths:
            if os.path.exists(p):
                path = p
                break

        if path is None:
            raise Exception(
                "TShark not found. Try adding its location to the configuration file. "
                "Searched these paths: {}".format(possible_paths)
            )
        print("Launching tshark")  
        timeout=self.timeout
        OUT_FILE=os.path.abspath(f"{OUT_FOLDER}/capture.cap")
        self.process = Popen([
            f"-i{SNIFF_INTERFACE}",
            #f"-aduration:{timeout}" ,
            f"-tad",
            f"-Tjson"
        ],executable=f"{path}", stdout=PIPE, stderr=PIPE, stdin=PIPE)


    def wrap_function(self, fn, *args, **kwargs):
    
        r = fn(*args, **kwargs)
        
if __name__ == "__main__":
    N=20
    pop = "bma"
    port=1625
    _, delta = check_version(pop, port, "/", True, None)

    shark = WireSharkSniffer(timeout=delta*N*0.000001 + 1)
    future = pool.apply_async(shark.capture_packages, args=("192.168.10.168", "157.52.95.25"))
    time.sleep(2) # give time to dump

     #reallylongkeythatmaytakesometimetoprocessbeacuseisquitelargeandcomplex

    for i in range(N): #4480
        #time.sleep(1)
        check_version(pop, port, "/reallylongkeythatmaytakesometimetoprocessbeacuseisquitelargeandcomplex", True, None)
        printProgressBar(i, N - 1)

    time.sleep(1)
    content=future.get()
    #print(content)
    filtered=shark.check_and_filter_events_order(content)

    print(len(filtered))
    #print(json.dumps(content, indent=4))
    