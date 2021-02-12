# Notes on timing measurement


# TODO
- Try sleep operations in the Fastly service
 - If not, measure then by number of operations
 - 

# RQs

- Is the precision of the timing measurements constant over all POPs and machines?
    - First answer for machines, 2000 machines, 77 POPs, 100000 samples, 
- Is synchronous better than concurrent approach of Van Goethem et al. ?
    -   Theoretically the removal of layers would remove jitter and latency


closer POP bma at fixed ip:
Binary search to locate the number of perceptible iterations
- LOOP at 1000 iterations with println is perceptible
    - home [] loop2 []
    - 
- LOOP at 5500 iterations with println is perceptible and considerable
- LOOP at 10000 iterations with println is perceptible and considerable

Binary search to locate the number of perceptible iterations
- LOOP at 1000 iterations calculating sum is perceptible
- LOOP at 5500 iterations calculating sum is perceptible but not considerable

Different POPs
  - bma:
    - L-Estimator midsummary for differences between `home` and `loop2` (1000 sums) gives 1.5 operations for 1000 samples
  - bog:
    - L-Estimator midsummary for differences between `home` and `loop2` (1000 sums) gives 0.5 operations for 1000 samples