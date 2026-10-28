# Julia fixture provenance

`sensor-calibration.csv` is an original, synthetic eight-record sensor-calibration example. No external dataset, real person or workplace source is represented. Its stable IDs, train/development/final labels and feature/label availability dates are part of the teaching contract.

The capstone embeds exactly these bytes so that its browser pad is self-contained. Its independent checker compares the embedded constant to this file. It also changes final outcomes to prove that final data does not choose the penalty, and injects duplicate IDs, late features, unavailable labels, changed split counts and nonfinite values to verify rejection.

The final two observations provide an exact numerical example, not a representative deployment study. The decision record hashes the fixture bytes and describes that limitation. `reference-contracts.json` binds generated reference source hashes and expected markers; hashes establish identity, not scientific correctness.
