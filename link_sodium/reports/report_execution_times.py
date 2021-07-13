import sys
import os
import re
import json
import matplotlib.pyplot as plt

from common import *
import matplotlib as mpl
import os

mpl.use('macOsX')

BASE_DIR=os.path.abspath(os.path.dirname(__file__))
latexify(5.5, 7, tick_size=9)

def wrapto(str, size=10):

    result = ""
    l = 0
    for s in str:
        result += s
        l += 1

        if l == size:
            result += "\n"
            l = 0

    return result


def process(jsonData):

    fig, ax = plt.subplots()
    format_axes(ax, hide=['top', 'right'], show=['bottom', 'left'])

    datas = [

    ]
    labels = [

    ]

    for function_name, results  in jsonData.items():
        print(function_name)

        timesN1 = results['nonInstrumented']["times"]
        timesOriginal = results['original']["times"]
        datas.append((
            timesOriginal,
            timesN1
        ))
        labels.append(function_name)


    l1=ax.violinplot([
        d[0] for d in datas
    ], positions=[i + 0.2 for i in range(len(datas))], widths=0.3, showmeans=True, vert=False)

    l2=ax.violinplot([
        d[1] for d in datas
    ], positions=[i - 0.2 for i in range(len(datas))], widths=0.3, showmeans=True, vert=False)

    ax.legend([
        l1['bodies'][0], l2['bodies'][0]
    ], [
        "Original",
        "Multivariant"
    ])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels([wrapto(s, size=20) for s in labels],  wrap=True)
    ax.set_xlabel("Execution time (ns)")
    ax.set_ylabel("Function name")


    fig.tight_layout()

    plt.savefig(f"{BASE_DIR}/out/times.pdf")

if __name__ == '__main__':
    data = json.loads(open(sys.argv[1], 'r').read())
    process(data)