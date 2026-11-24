"""Fenced evidence-record sketches for the reading-only JAX units.

Each reading unit carries one sketch per worked example. A sketch shows the shape of the
record a learner would keep, with every unobserved stage written as missing or pending.
None of these values come from a real device run.
"""

RECORDS: dict[int, tuple[str, ...]] = {
    32: (
        """record: hypothetical partial GPU probe
source identity ........ commit and file path retained
package import ......... observed
device inventory ....... one GPU listed
explicit placement ..... missing
synchronized compute ... missing
host readback .......... missing
supported claim ........ package and device discovery only""",
        """probe: square of [1, 2, 3] on one requested GPU
request backend ........ gpu, fail if absent
versions ............... jax, jaxlib, plugin and driver recorded
placement .............. literal vector put on the selected device
compute ................ x * x compiled, then block_until_ready
result device .......... must match the requested device
oracle ................. host values must equal [1, 4, 9]
failures and cleanup ... kept in the record, never dropped""",
    ),
    33: (
        """global mean across two participants
process 0 .............. local sum 6, local count 3
process 1 .............. local sum 10, local count 1
collective sum ......... 6 + 10 = 16 on both processes
collective count ....... 3 + 1 = 4 on both processes
global mean ............ 16 / 4 = 4, replicated
mean of local means .... (2 + 10) / 2 = 6, a different question""",
        """divergent participation review
process 0 path ......... enters psum on axis replica
process 1 path ......... branch skips the psum
expected outcome ....... collective cannot complete as written
local numeric checks ... do not qualify participation
repair ................. hoist psum out of the branch, or send a neutral 0
test boundary .......... bounded timeout on owned processes only""",
    ),
    34: (
        """custom affine operator review
forward, contiguous float32 ...... observed correct
forward, transposed input ........ untested
unsupported dtype rejection ...... untested
backward rule .................... untested
synchronization and errors ....... untested
performance ...................... unmeasured
current claim .................... one narrow forward case""",
        """backward rule check for y = 3x + 1
local derivative dy/dx ........... 3
incoming cotangent ............... 4
required input cotangent ......... 3 * 4 = 12
defective rule returns ........... 4, the cotangent unchanged
why unit fixtures hide it ........ cotangent 1 and scale 1 give equal answers
next fixture ..................... change the scale and use a non-unit cotangent""",
    ),
}
