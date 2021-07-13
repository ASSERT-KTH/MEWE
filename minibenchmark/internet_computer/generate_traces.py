import os
import random

if __name__ == "__main__":

    # generate 100 traces, for a 100*50 comparisons
    for i in range(100):
        # trace size between 50 and 1000 symbols between 0 and 255
        tr = open(f"test_traces/{i}.trace.txt", 'w')
        
        size = random.randint(50, 1000)
        for j in range(size):
            s = random.randint(0, 254)
            tr.write(f"{s}, ")