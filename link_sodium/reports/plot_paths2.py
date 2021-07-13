import csv
import os
import matplotlib.pyplot as plt
from subprocess import check_output
import sys
import json
import matplotlib
from common import *

cmap = matplotlib.cm.get_cmap('tab20')
if __name__ == "__main__":


    # TODO, receive functionmap and csv file from sys.argv

   

    d = json.loads(open(sys.argv[1], 'r').read())
    map, reverse_map = parse_map(sys.argv[2])

    #print(map)
    

    # export d3 data
    '''
    var data = [{ "name": "A", "group": 1 }, { "name": "B", "group": 1 }, { "name": "C", "group": 1 }, { "name": "D", "group": 1 }, { "name": "E", "group": 1 }, { "name": "F", "group": 1 },
    { "name": "G", "group": 2 }, { "name": "H", "group": 2 }, { "name": "I", "group": 2 }, { "name": "J", "group": 2 }, { "name": "K", "group": 2 }, { "name": "L", "group": 2 },
    { "name": "M", "group": 3 }, { "name": "N", "group": 3 }, { "name": "O", "group": 3 }]
    '''

    groups, groupCount = group_functions_by_name(reverse_map.keys())

    result = {

    }
    #S=sorted(set(Xs))
    #Expanded=[]

    colors = [ "%s"%(matplotlib.colors.rgb2hex(cmap(i/groupCount)),) for i in range(groupCount) ]

    #rnge = list(range(len(set(Xs))))

    # Filter reversed map

    # Create links

    links = {

    }

    data = []
    edges = []
    pops = {}

    for function in d.keys():

        if function == sys.argv[3]:
            instrumented = d[function][sys.argv[4]]
            paths = instrumented["paths"]

            for pop in paths.keys():
                # add pop as -1 group node
                if pop not in pops:
                    data.append({
                        'name': pop,
                        'group': 0,
                        'order': 0,
                        'id': pop
                    })
                    pops[pop] = True
                stacktrace = paths[pop]["path"]
                previous = pop

                for n in stacktrace:

                    links[f"{previous}{n}"] = [ previous, n ]
                    previous = n

    pcolors = ["%s"%(matplotlib.colors.rgb2hex(cmap(i/len(pops))),) for i in range(len(pops))]

    visited = set()
    for e in links.values():
        p, c = e
        pname = map[p] if p in map else p
        cname = map[c] if c in map else c
        edges.append(
            {
                'source': pname,
                'target': cname,
                'value': 1,
                'order': 100
            }
        )
        visited.add(pname)
        visited.add(cname)

    for e, v in reverse_map.items():
        if e in visited:
            data.append({
                'name': e,
                'group': reverse_map[e]['group'],
                'id': e,
                'pop': reverse_map[e]['pop']
            })

    result['data'] = data
    result['colors'] = colors
    result['pcolors'] = colors
    result['edges'] = edges
    #result['range'] = rnge
    S = set([r['group'] for r in reverse_map.values()])
    result['groups'] = list(S)
    result['clusters'] = [i*100 for i in range(len(S))]

    open("%s.d3.json"%(sys.argv[1]), 'w').write(json.dumps(result))

    c=open("template2.html", "r").read()
    R=c.format(
        R=json.dumps(result)
    )

    open(f"%s.html"%(sys.argv[3]), 'w').write(R)