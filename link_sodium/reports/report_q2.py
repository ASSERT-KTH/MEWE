import json
import sys
from matplotlib import pyplot as plt
import numpy as np
from common import *
import matplotlib as mpl
import os

mpl.use('macOsX')

BASE_DIR=os.path.abspath(os.path.dirname(__file__))
latexify(12, 5)


def reportSizes(data, relative=True, section="code_section_size", do_set_analysis=False, title="Relative code section size"):
    labels = []
    sizes  = []

    all_sets = []

    for function_name, results in data.items():
        labels.append(function_name)

        original, instrumented, nonInstrumented = results['original'], results['instrumented'], results['nonInstrumented']
        sizes.append((
            original['meta'][section],
            instrumented['meta'][section],
            nonInstrumented['meta'][section],
        ))

        functionNames = nonInstrumented["meta"]["exported_function_names"]
        all_sets.append((function_name, set(
            [f[1] for f in functionNames]
        )))

        print(sizes[-1][0], sizes[-1][2], sizes[-1][2] - sizes[-1][0],
            len([f[1] for f in functionNames]))


        #print(all_in)
        #print(len(all_in))

    if do_set_analysis:
        for i, s in enumerate(all_sets):
            print()
            for j in range(i + 1, len(all_sets)):
                s1 = s[1]
                s2 = all_sets[j][1]
                #print(s1 - s2, end=" ")
                print(len(s2.intersection(s1)), len(s1), len(s2), end=" ")
    fig, ax = plt.subplots()

    format_axes(ax, hide=['top', 'right'], show=['bottom', 'left'])
    originalSizes = [s[0] for s in sizes]
    n1Sizes = [s[2] for s in sizes]

    idxs = np.arange(len(labels))
    width = 0.35

    if not relative:
        ax.bar(idxs + width/1.5, originalSizes, width, label="Original")
        ax.bar(idxs - width/1.5, n1Sizes, width, label="N1 diversifier")
    else:
        relativeSize = [s[2]/s[0] for s in sizes]
        ax.bar(idxs + width/1.5, [1]*len(idxs), width, label="Original")
        ax.bar(idxs - width/1.5, relativeSize, width, label="N1 diversifier")

    ax.set_xticks(idxs)
    ax.set_xticklabels(labels, rotation='45', horizontalalignment='right')
    ax.legend(bbox_to_anchor = (1, 1))
    ax.set_title(title)

    ax.set_xlabel("Function name")
    ax.set_ylabel("Relative code section size")

    fig.tight_layout()
    #plt.show()
    plt.savefig(f"{BASE_DIR}/out/{section}.pdf")


def reportOverallSize(data, relative=True):
    labels = []
    sizes  = []

    all_sets = []

    for function_name, results in data.items():
        labels.append(function_name)

        original, instrumented, nonInstrumented = results['original'], results['instrumented'], results['nonInstrumented']
        sizes.append((
            original['packageSize'],
            instrumented['packageSize'],
            nonInstrumented['packageSize'],
        ))

    fig, ax = plt.subplots()
    latexify(12, 5)

    format_axes(ax, hide=['top', 'right'], show=['bottom', 'left'])
    originalSizes = [s[0] for s in sizes]
    n1Sizes = [s[2] for s in sizes]

    idxs = np.arange(len(labels))
    width = 0.35

    if not relative:
        ax.bar(idxs + width/1.5, originalSizes, width, label="Original")
        ax.bar(idxs - width/1.5, n1Sizes, width, label="N1 diversifier")
    else:
        relativeSize = [s[2]/s[0] for s in sizes]
        ax.bar(idxs + width/1.5, [1]*len(idxs), width, label="Original")
        ax.bar(idxs - width/1.5, relativeSize, width, label="N1 diversifier")
        print(relativeSize)

    ax.set_xticks(idxs)
    ax.set_xticklabels(labels, rotation='45', horizontalalignment='right')
    ax.legend(    bbox_to_anchor = (1, 1))
    ax.set_xlabel("Function name")
    ax.set_ylabel("Relative package size")
    ax.set_title("Relative package size")
    fig.tight_layout()
    #plt.show()
    plt.savefig(f"{BASE_DIR}/out/package.pdf")

if __name__ == '__main__':
    jsonReport = sys.argv[1]
    jsonReport = open(jsonReport, 'r').read()
    jsonReport = json.loads(jsonReport)

    print("Code size")
    reportSizes(jsonReport, section="code_section_size", do_set_analysis=True)
    print("Type size")
    reportSizes(jsonReport, section="type_section_size", title="Type section size")
    print("Function size")
    reportSizes(jsonReport, section="function_section_size", title="Function section size")
    print("Element size")
    reportSizes(jsonReport, section="element_section_size", title="Element section size")
    print("Data size")
    reportSizes(jsonReport, section="data_section_size", title="Data section size")
    print("Global size")
    reportSizes(jsonReport, section="global_section_size", title="Global section size")
    print("memory size")
    reportSizes(jsonReport, section="memory_section_size", title="Memory section size")
    print("Table size")
    reportSizes(jsonReport, section="table_section_size", title="Table section size")
    print("Import size")
    reportSizes(jsonReport, section="import_section_size", title="Import section size")

    reportOverallSize(jsonReport)

