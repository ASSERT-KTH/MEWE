import sys
import json


if __name__ == '__main__':
    popResults = json.loads(open(sys.argv[1], 'r').read())

    for i, k in enumerate(popResults):
        print(f"\"{k['code']}\" => {i},")