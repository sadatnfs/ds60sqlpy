"""tf-009: Batches and repeated updates.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count updates
# Partition IDs 1..6 into batches of size two; retain each batch and count one update per
# batch.
# Expected: batches [[1,2],[3,4],[5,6]] and 3 updates.

# Exercise 2: Retain a remainder
# Partition five IDs by two and compare with explicitly dropping the short batch.
# Expected: sizes [2,2,1]; dropping retains only IDs1..4.

# Exercise 3: Trace weight state
# Implement three batch updates for x=1..6,y=2x,w=0,rate=.01; record the weight before
# each update.
# Expected: 3 finite, nonidentical updated weights.

# Exercise 4: Compare batch policies
# Repeat one epoch with sizes one and three from exactly w=0; compare update counts and
# endpoint weights.
# Expected: 6 versus2 steps and different endpoint weights.

# Exercise 5: Preserve pairs
# Shuffle IDs with permutation [5,0,4,1,3,2] and apply the same permutation to inputs and
# targets.
# Expected: Every shuffled target equals twice its paired input.

# Exercise 6: Aggregate unequal batches
# Combine batch mean losses2 and8 with counts2 and1; compare mean-of-means with the record
# mean.
# Expected: record mean4; unweighted batch mean5.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
