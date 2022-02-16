import sys
from latexify.common import *
from itertools import zip_longest
import matplotlib.pyplot as plt

def get_size(wasmfile):
    return len(open(wasmfile, 'rb').read())

if __name__ == "__main__":
    tpe = sys.argv[1]
    originals = sys.argv[2::3]
    multivariants = sys.argv[3::3]
    names = sys.argv[4::3]

    latexify(fig_width=3.5, fig_height=2)

    tuples = zip_longest(originals, multivariants, names)

    sizes = [
        (
            get_size(original),
            get_size(multivariant),
            name

        ) for original, multivariant, name in tuples
    ]

    fig, ax = plt.subplots()
    format_axes(ax, show=['left', 'bottom'], hide=['top', 'right'])
    ax.bar(
        range(len(sizes)),
        [t[0] if tpe != "percent" else 100 for t in sizes],
        width=0.4 # original size
    )
    ax.bar(
        [0.5 + x for x in range(len(sizes))],
        [t[1] if tpe != "percent" else 100*t[1]/t[0] for t in sizes],
        width=0.4 # multivariant size
    )

    ax.set_xticks([0.25 + x for x in range(len(sizes))])
    ax.set_ylabel("Binary size (bytes)" if tpe != "percent" else "Relative size")
    ax.set_xticklabels(
        [t[2].replace("_", "\_") for t in sizes],
        rotation=45
    )
    ax.legend([
            "Original binary",
            "Multivariant binary"
        ], bbox_to_anchor = (0.5, 1)
    )

    print(list(zip([t[1] if tpe != "percent" else 100*t[1]/t[0] for t in sizes], sizes),
        ))
    plt.tight_layout()

    plt.savefig(f"out/sizes.pdf")
