# Independent convex target references

`build_oracles.py` enumerates sign and box active sets, solves their KKT equations
with exact rational arithmetic, and checks positive definiteness exactly. It does
not duplicate the proximal iteration. Its nine small convex cases cover selected
nonzero-centered Gaussian terms, exact L1 zeros, cross-coupling, fixed nuisance
coordinates, box normal cones and weight normalization.

From the package directory:

```sh
python3 jvm/oracles/build_oracles.py
python3 jvm/oracles/emit_scala_fixtures.py
python3 -m unittest discover -s jvm/oracles -p 'test_*.py' -v
```

The emitter creates test data for `RegularizationOracleChecks`; it does not compile
or run Scala. Host mathematical checks, JVM solver checks, native worker checks
and actual distributed Spark acceptance are separate evidence. These strictly
convex quadratic examples do not establish global optimality for nonlinear or
Laplace marginal likelihoods.

The canonical plan digests are independently encoded using big-endian lengths,
UTF-8 and IEEE754 binary64 values with normalized signed zero. They bind model
and coordinate/penalty/constraint definitions. Complete evaluation/posterior
receipts additionally need the real artifact and data/weight ledger.
