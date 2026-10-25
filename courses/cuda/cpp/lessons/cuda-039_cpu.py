"""cuda-039: answer-free CPU model practice."""

# CPU model practice: Streams as dependency-ordered work queues
# Reconstruct the first worked model and its stated assertions in this lesson's saved
# pad.
# Then extend your own code for Exercise 3: Draw the event edge for upload in A followed
# by compute in B.
# Check the boundary from Exercise 5: How should an empty chunk affect the queue?
# These are supplied literal fixtures, not a completed algorithm or CUDA execution.

x = [1, 2, 3]
edges = [("produce_A", "record_event"), ("record_event", "wait_B"), ("wait_B", "consume_B")]

raise NotImplementedError("Implement the CPU model and boundary assertions above.")
