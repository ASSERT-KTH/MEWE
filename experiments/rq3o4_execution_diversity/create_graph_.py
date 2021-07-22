import sys
import os
import json

from utils.utils import *

if __name__ == "__main__":

    fmap, reversed = parse_map(sys.argv[1])
    fname = sys.argv[3]
    edges = create_graph_from_wasm(sys.argv[2], fname)

    #for e in edges.keys():
    #    for e2 in edges[e].keys():
    #        print(f"{e} -> {e2}")