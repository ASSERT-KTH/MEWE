import sys
import json
from common import *
import matplotlib.pyplot as plt
import os
from subprocess import check_output
import math
import numpy as np

latexify(15, 5)
BASE_DIR=os.path.abspath(os.path.dirname(__file__))

def draw_visit_matrix(jsonData,compress=True, mapfile=None, correlation=None):

    def get_px(A, k, avg_size=100):

       # print(A[k], avg_size)
        return A[k]/avg_size#sum([A[n] for n in A.keys()])

    def get_freqs(path):
        R = {}

        for n in path:
            if n not in R:
                R[n] = 0
            R[n] += 1

        return R

    def add_edge(OVERALL_MATRIX, n1, n2, ALL_IDS=None):

        if ALL_IDS is not None:
            if n1 not in ALL_IDS:
                ALL_IDS[n1] = 0

            if n2 not in ALL_IDS:
                ALL_IDS[n2] = 0

            ALL_IDS[n1] += 1
            ALL_IDS[n2] += 1

        if n1 not in OVERALL_MATRIX:
            OVERALL_MATRIX[n1] = { }

        if n2 not in OVERALL_MATRIX[n1]:
            OVERALL_MATRIX[n1][n2] = 0

        OVERALL_MATRIX[n1][n2] += 1

    fig, ax = plt.subplots()
    format_axes(ax, hide=['top', 'right'], show=['bottom', 'left'])
    values = [

    ]
    labels = []
    for fname, data in jsonData.items():
        labels.append(fname)
        DOT_CONTENT=""
        print(fname, end=" ")
        DOT_CONTENT += "digraph ST {\n"
        DOT_CONTENT += "size=\"9.3,9.3!\" ratio=fill;\n"
        DOT_CONTENT += "graph [splines=ortho, dpi=300]\n"
        DOT_CONTENT += "node [shape=box]\n"
        DOT_CONTENT += "rankdir=LR;\n"
        paths = data['instrumented']["paths"]

        D = {

        }

        A = {

        }

        freqs = []
        for pop, d in paths.items():
            path = d["path"]

            if not path:
                continue
            entry = path[0]

            if int(entry) in mapfile:
                entry = mapfile[int(entry)]

            add_edge(D, pop, entry)
            prev = entry
            for i in range(1, len(path)):
                n1 = path[i]

                if int(n1) in mapfile:
                    n1 = mapfile[int(n1)]


                add_edge(D, prev, n1, A)

                prev = n1
            
            freqs.append(
                get_freqs(path)
            )

        OVERALL_FREQ = {}
        SUM = 0
        for k in freqs:
            for i, f in k.items():
                if i not in OVERALL_FREQ:
                    OVERALL_FREQ[i] = 0
                OVERALL_FREQ[i] += f
                SUM += f
        # Shannon entropy

        S = 0
        
        for k in OVERALL_FREQ.keys():
            px1 = OVERALL_FREQ[k]/SUM
            #print(px1)
            S += (px1*math.log(px1,math.e))

        print("Entropy", -1*S)
        values.append((
            correlation[fname], S
        ))

        for n1 in D.keys():
            for n2 in D[n1].keys():
                label=D[n1][n2]
                nn1 = n1.__str__().replace(".", "_")
                nn2 = n2.__str__().replace(".", "_")
                
                DOT_CONTENT += f"{nn1} -> {nn2} [xlabel=\"{label}\"] ;\n"

        DOT_CONTENT += "}\n"
        open(f"{BASE_DIR}/out/{fname}.dot", 'w').write(DOT_CONTENT)

        # call graphviz
        check_output([
            "dot",
            "-Tpng",
            f"{BASE_DIR}/out/{fname}.dot",
            "-o",
            f"{BASE_DIR}/out/{fname}.png"
        ])

    ax.scatter(
        [v[0] for v in values],
        [v[1] for v in values],
    )

    for i, v in enumerate(values):
        ax.text(v[0], v[1], labels[i])

    plt.savefig(f"{BASE_DIR}/out/correlation.pdf")
def draw_tree(jsonData,compress=True, mapfile=None):

    for fname, data in jsonData.items():
        DOT_CONTENT=""
        print(fname)
        DOT_CONTENT += "digraph ST {\n"

        DOT_CONTENT += "graph [splines=ortho]\n"
        DOT_CONTENT += "node [shape=box]\n"
        DOT_CONTENT += "rankdir=LR;\n"
        paths = data['instrumented']["paths"]

        for pop, d in paths.items():
            path = d["path"]
            entry = path[0]

            if int(entry) in mapfile:
                entry = mapfile[int(entry)]

            DOT_CONTENT += f"{pop} -> {entry};\n"
            DOT_CONTENT += f"{entry} -> "

            compressed = []
            prev = None
            for i in path:
                if i != prev:
                    compressed.append(i)
                    prev = i

            D = compressed if compress else path

            for i in range(1, len(D)):
                n1 = path[i]

                if int(n1) in mapfile:
                    n1 = mapfile[int(n1)]

                DOT_CONTENT += f"{n1} -> "

            DOT_CONTENT += " end ;\n"

        DOT_CONTENT += "}\n"

        open(f"{BASE_DIR}/out/{fname}.dot", 'w').write(DOT_CONTENT)

def process(jsonData ,compress=False, mapfile=None):



    for function_name, results  in jsonData.items():
        print(function_name)

        fig, ax = plt.subplots()
        paths = results['instrumented']["paths"]
        format_axes(ax, hide=['top', 'right', 'bottom', 'left'])
        printed = False
        for pop, path in paths.items():
            ids = [int(i) for i in path["path"]]
            if not printed:
                print(len(ids))

                printed = True
            compressed = []

            prev = None
            for i in path:
                if i != prev:
                    compressed.append(i)
                    prev = i

            if compress:
                ax.plot(
                    range(len(compressed)),
                    compressed,
                    '--o',
                    color='C0',
                    alpha=0.1
                )
            else:

                ax.plot(
                    range(len(ids)),
                    ids,
                    '--o',
                    color='C0',
                    alpha=0.1
                )

                #if mapfile:
                #    for x, id in enumerate(ids):
                #        ax.text(x, id, mapfile[id])

        ax.set_xticks([])
        ax.set_yticks([])
        #ax.set_yscale("log")

        ax.axis("off")
        fig.tight_layout()
        plt.savefig(f"{BASE_DIR}/out/{function_name}.xpath.pdf")


if __name__ == '__main__':
    data = json.loads(open(sys.argv[1], 'r').read())

    CORRELATIONS = {
        'bin2base64': 42,
        'crypto_aead_chacha20poly1305_ietf_decrypt_detached': 27,
        'crypto_aead_chacha20poly1305_ietf_encrypt_detached': 24,
        'crypto_core_ed25519_scalar_complement': 81,
        'crypto_core_ed25519_scalar_random': 133,
        'crypto_core_ed25519_scalar_invert': 28,
        'sodium_add': 50,
        'sodium_is_zero': 95,
        'sodium_memcmp': 102,
        'sodium_increment': 118,
    }

    if len(sys.argv) > 2:
        functionMap = parse_map(sys.argv[2])
        draw_visit_matrix(data, mapfile=functionMap, correlation=CORRELATIONS)
    else:
        draw_visit_matrix(data)
