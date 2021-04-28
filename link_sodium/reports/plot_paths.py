import csv
import os
import matplotlib.pyplot as plt
from subprocess import check_output
import sys
import json
import matplotlib

cmap = matplotlib.cm.get_cmap('tab20')

# TODO, receive functionmap and csv file from sys.argv

Xs = []

entry = {

}

fig, axis = plt.subplots(figsize=(14,7))
ax1 = axis
graph = ""

with open(sys.argv[1]) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        popname, path = row[0], row[1:]

        #for edge  in path:
        if path[0] not in entry:
            entry[path[0]] = []
        entry[path[0]].append(popname)

        compressed = []

        prev = None
        for i in path:
            if i != prev:
                compressed.append(i)
                prev = i
            
        Xs.append(int(path[0]))
        graph += " -> ".join(path)
        graph += ";\n"

        ax1.plot(
            range(len(compressed)),
            compressed,
            '--o',
            label=popname,
            color='C0',
            alpha=0.2
        )
    #ax2.hist(Xs, bins=len(set(Xs)), histtype='step')

print(entry)
ax1.set_title("%s"%(sys.argv[1],))
ax1.axis("off")
#ax2.axis("off")

#axis.get_xaxis().set_visible(False)
#axis.get_yaxis().set_visible(False)
ax1.set_xticks([])
#ax2.set_xticks(range(len(set(Xs))))
ax1.set_yticks([])
#g = open("g.dot", 'w')
#g.write("digraph {\n")
#g.write(graph)
#g.write("}")

#print(entry)

#plt.legend()
plt.tight_layout()
plt.savefig(sys.argv[1] + "paths.png", dpi=400)


# export d3 data
'''
var data = [{ "name": "A", "group": 1 }, { "name": "B", "group": 1 }, { "name": "C", "group": 1 }, { "name": "D", "group": 1 }, { "name": "E", "group": 1 }, { "name": "F", "group": 1 },
{ "name": "G", "group": 2 }, { "name": "H", "group": 2 }, { "name": "I", "group": 2 }, { "name": "J", "group": 2 }, { "name": "K", "group": 2 }, { "name": "L", "group": 2 },
{ "name": "M", "group": 3 }, { "name": "N", "group": 3 }, { "name": "O", "group": 3 }]
'''

result = {

}
S=sorted(set(Xs))
Expanded=[]

for s in S:
    for _ in range(1):
        Expanded.append(s)
colors = [ "%s"%(matplotlib.colors.rgb2hex(cmap(Expanded.index(i)/len(set(S)))),) for i in S ]

rnge = list(range(len(set(Xs))))

data = []
for e in entry:
    for pop in entry[e]:
        data.append({
            'name': pop,
            'group': int(e)
        })

result['data'] = data
result['colors'] = colors
result['range'] = rnge
result['groups'] = list(S)
result['clusters'] = [i*60 for i in range(len(S))]

open("%s.d3.json"%(sys.argv[1]), 'w').write(json.dumps(result))

c=open("template.html", "r").read()
R=c.format(
    R=json.dumps(result)
)

open(f"%s.html"%(sys.argv[1]), 'w').write(R)