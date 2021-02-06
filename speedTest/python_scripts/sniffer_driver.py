import time
import pyshark
from common import *
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

    def check_and_filter_events_order(self, events, src="", dst=""):

        last = 0
        filtered = []

        port_pairs = dict()

        for event in events:
            #print(event)
            if "TSval" in event["arguments"]:
                time = event["arguments"]["TSval"]
                time = int(time)
                event["arguments"]["TSval"] = time
                fromP = event["src_port"]
                toP = event["dst_port"]
                port_pair=int(fromP)*int(toP)

                if port_pair not in port_pairs:
                    port_pairs[port_pair] = []

                if time < last:
                    pass
                    #print(filtered)
                    #print(event, last)
                    #raise Exception("Invalid time order")

                last = time
                port_pairs[port_pair].append(event)
        print(f"Pairs {len(port_pairs)}")
        # Remove interaction without 0 TSrec in the first event

        tvals = [] # TODO Check time unit
        tdates = []
        for interaction in list(port_pairs.values())[:-2]: # Always discard last package
            if interaction[0]["arguments"]["TSecr"] == 0:
                print("Interaction has no first package")
                continue
            first_TSval = 0
            date = datetime.datetime.now()
            delta = 0

            for event in interaction:
                fr, to, actions, arguments, ts, tec = event["src_ip"], event["dst_ip"], event["actions"], event["arguments"], event["arguments"]["TSval"], event["arguments"]["TSecr"]

                if fr == dst:
                    #print(event)
                    date = datetime.datetime.strptime("%s %s"%(event["date"], event["time"]), '%Y-%m-%d %H:%M:%S.%f')
                    if first_TSval == 0:
                        first_TSval = ts

                        first_date = date
                    delta = ts - first_TSval

                    print(f"{fr} {to} {actions} {ts} {tec}")
            #print(delta)
            tvals.append(delta)
            tdates.append((date - first_date).microseconds)
        #print(len(port_pairs.keys()))
        return tvals, tdates

    def filter_packages(self, content, src, dst, only_tcp=True):
        packages = content.split("\n")

        events = []
        parser = self.event_parser
        argument_parser=re.compile(r" (?P<name>\w+)=(?P<value>\d+)")

        for p in packages:
            sanitized=p.strip()
            m = parser.search(sanitized)

            if m:
                #print(m.group("id"), m.group("date"), m.group("time"), m.group("src_ip"), m.group("dst_ip"), m.group("protocol"), m.group("src_port"), m.group("dst_port"), m.group("actions"), m.group("arguments"))

                event = dict()
                event["id"] = m.group("id")
                event["date"] = m.group("date")
                event["time"] = m.group("time")
                event["src_ip"] = m.group("src_ip")
                event["dst_ip"] = m.group("dst_ip")
                event["protocol"] = m.group("protocol")
                event["src_port"] = m.group("src_port")
                event["dst_port"] = m.group("dst_port")
                #event["tail"] = m.group("tail")
                event["actions"] = [t.strip() for t in m.group("actions")[1:-1].split(",")]
                event["arguments"] = dict()

                for argmatch in argument_parser.finditer(m.group("arguments")):
                    event["arguments"][argmatch.group("name")] = argmatch.group("value")

                if only_tcp and event["protocol"] != "TCP":
                    continue

                #print(event["src_ip"], event["dst_ip"])
                if (event["src_ip"] == src and event["dst_ip"] == dst) or (event["src_ip"] == dst and event["dst_ip"] == src):
                    print(p)
                    events.append(event)
            
        # 1 2021-02-05 16:01:27.659706 192.168.10.168 → 157.52.95.25 TCP 78 59973 → 443 [SYN] Seq=0 Win=65535 Len=0 MSS=1460 WS=64 TSval=524707847 TSecr=0 SACK_PERM=1
        print(len(events))
        return events

    def capture_packages(self):
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
        ], executable=f"{path}", stdout=PIPE, stderr=PIPE, stdin=PIPE)


        std, err = process.communicate()
        #print(err.decode(), std.decode())
        return std.decode()

        if err:
            print(f"Stopping {err.decode()}")

        data = json.loads(std)
        for p in data:
            # Filtering IP host and dst
            
            layers = p["_source"]["layers"]
            frame_time_stamp = layers["frame"]["frame.time"]
            if "ip" in layers:
                ip_layer = layers['ip']
                src_ip = ip_layer["ip.src"]
                dst_ip = ip_layer["ip.dst"]
                
                if "tcp" in layers and "tcp.options_tree" in layers["tcp"]:
                    tvsal = layers["tcp"]["tcp.options_tree"]["tcp.options.timestamp_tree"]["tcp.options.timestamp.tsval"]

                    if (src_ip in options.src_filter and dst_ip in options.dst_filter) or (src_ip in options.dst_filter and dst_ip in options.src_filter):
                        print(json.dumps(p))
                        print(src_ip, dst_ip, frame_time_stamp, tvsal)
    def wrap_function(self, fn, *args, **kwargs):
    
        r = fn(*args, **kwargs)
        
if __name__ == "__main__":
    N=20000
    pop = "bma"
    port=1625
    _, delta = check_version(pop, port, "/", True, None)

    shark = WireSharkSniffer(timeout=delta*N*0.000001 + 1)
    future = pool.apply_async(shark.capture_packages)
    time.sleep(2) # give time to dump

     #reallylongkeythatmaytakesometimetoprocessbeacuseisquitelargeandcomplex

    for i in range(N): #4480
        check_version(pop, port, "/reallylongkeythatmaytakesometimetoprocessbeacuseisquitelargeandcomplex", True, None)
        printProgressBar(i, N - 1)

    time.sleep(1)
    content=future.get()
    events=shark.filter_packages(content, "192.168.10.168", "157.52.95.25")
    #print(events)
    rtts, dates = shark.check_and_filter_events_order(events, "192.168.10.168", "157.52.95.25")
    print(rtts, dates, np.mean(dates))

    import matplotlib.pyplot as plt
    plt.hist(dates, bins=(len(set(dates))))
    plt.show()