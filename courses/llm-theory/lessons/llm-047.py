"""llm-047: Sparse experts, routing capacity and load balancing.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate a top2 expert mixture
# UseexpertsI, 2I, -I andthree token/router rows with selected probabilities3/4 and1/4.
# Expected: outputs[1.25, 0], [0, 1.75], [-.25, -.25].

# Exercise 2: Enforce expert capacity with residual fallback
# Routefourtokens toexperts0, 0, 1, 0 withcapacity2 andunit top1 gates.
# Expected: assignedcounts3, 1; accepted2, 1; lasttoken drops its expert delta andkeeps its input.

# Exercise 3: Compute a load-balancing term
# Usehard fractionsf[.75, .25], mean routerprobabilitiesP[.7, .3], expertcount2
# andcoefficient.01.
# Expected: auxiliaryloss.012; balancedfixture.01.

# Exercise 4: Trace a local router gradient
# Perturb thefirstlogit ofthefirsttop2mixture row without changing selectedexperts.
# Expected: derivative offirstoutputcoordinate is-3/16 within1e-8.

# Exercise 5: Separate total andactive parameter counts
# Use8two-layerexperts withwidth64, hidden128 andtop2activation, excludingrouter
# andbiases.
# Expected: total131072expertweights; 32768selectedexpertweights pertoken.

# Exercise 6: Validate routing policy andties
# Rejecttopk0 andcapacity0; checkequal routerlogits choose lowerindices deterministically.
# Expected: invalid policiesraiseValueError; top2tieindices0, 1.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
