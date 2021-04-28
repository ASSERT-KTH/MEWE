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

fig, axis = plt.subplots(figsize=(21,7))
ax1 = axis
graph = ""

COMPRESS=True

with open(sys.argv[1]) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:

        if len(row) < 3:
            continue
        
        popname, path = row[0], row[1:]

        print(popname, path)
        #for edge  in path:
        if path[0] not in entry:
            entry[path[0]] = []
        entry[path[0]].append(popname)

        compressed = []
        sizes = []

        prev = None
        size=1
        for i in path:
            if i != prev:
                compressed.append(i)
                prev = i
                sizes.append(size)
                size = 0

            size += 1
        Xs.append(int(path[0]))
        graph += " -> ".join(path)
        graph += ";\n"

        if COMPRESS:
            ax1.plot(
                range(len(compressed)),
                compressed,
                '--o',
                label=popname,
                color='C0',
                alpha=0.2
            )
            
            print("Ploting sizes")
            for i, s in enumerate(sizes):
                ax1.scatter(
                    i,
                    compressed[i],
                    s=2*s,
                    color='C2',
                    zorder=3
                )
        else:
            ax1.plot(
                range(len(path)),
                path,
                '--o',
                label=popname,
                color='C0',
                alpha=0.2
            )
        ax1.scatter(
            0,
            path[0],
            color='C1',
            zorder=3
        )
    #ax2.hist(Xs, bins=len(set(Xs)), histtype='step')

print(entry)
ax1.set_title("%s"%(sys.argv[1],))
ax1.axis("off")
ax1.grid(True)
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

