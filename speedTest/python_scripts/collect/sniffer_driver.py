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
        self.event_parser = re.compile(r'^(?P<id>\d+) (?P<date>\d\d\d\d-\d\d-\d\d) (?P<time>\d\d:\d\d:\d\d\.\d+) (?P<src_ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) → (?P<dst_ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (?P<protocol>\w+) (?P<process>\d+) (?P<src_port>\d+) → (?P<dst_port>\d+) (?P<actions>\[( ?\w+,?)+\])(?P<arguments>( ?\w+=\d+)+)')
        self.timeout=timeout

        print(f"Timeout {timeout}")

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

    def get_rtts_from_tcp(self, interactions, src_ip):
        result = []
        for interaction in interactions:
            first = 0
            s = 0
            for event in interaction: # Patch since for some reason the delay between requests is added to the interaction
                ip_layer = event["_source"]["layers"]["ip"]

                if ip_layer["ip.src"] == src_ip:
                    tcp_layer = event["_source"]["layers"]["tcp"]
                    if "tcp.options_tree" in tcp_layer:
                        tsval = tcp_layer["tcp.options_tree"]["tcp.options.timestamp_tree"]["tcp.options.timestamp.tsval"]
                        
                        if first == 0:
                            first += float(tsval)
                        else:
                            print(tsval, float(tsval) - first)
                            s += float(tsval) - first
                            first = float(tsval)
            result.append(s)
            #print(s)
        #print(result)
        return result

    def estimate_freq(self, interactions, discard_tail=0):
        #TODO
        pass
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
        process = Popen([
            f"-i{SNIFF_INTERFACE}",
            f"-aduration:{timeout}" ,
            f"-tad",
            f"-Tjson",
            f"-dtcp.port==443,http",
            f"-dtcp.port==80,http"
        ], executable=f"{path}", stdout=PIPE, stderr=PIPE, stdin=PIPE)


        std, err = process.communicate()
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
                
        return events

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
    