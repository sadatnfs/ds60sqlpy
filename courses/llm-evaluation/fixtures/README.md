# Evaluation fixtures

`evaluation-corpus.json` is authored synthetic data for the Research Support Desk case. Every correct/incorrect flag, confidence and latency is constructed for teaching. It is not an observation of a pretrained model or an external population. Requests are nested in families; split and label-availability fields make leakage and censoring visible. Programs embed their small relevant rows so the single-file worker needs no filesystem or network access outside its job.

`request_id` identifies a row, `family_id` the dependence/split unit, `segment` the target sampling stratum, `split` the development partition, `event_day` the decision time and `label_day` the first day its label may be inspected. Correctness is distinct from whether the candidate answered. A critical error is a separate gate, never averaged away. Each guide states which subset or counterexample it uses.

All authored requests are answerable under the fixture corpus. An abstention contributes zero delivered-answer correctness. Confidence and latency are constructed fields, not measurements from a model. Unit016 uses only the two held-out families and checks label availability at its cutoff; earlier training/development records remain excluded from that final packet.
