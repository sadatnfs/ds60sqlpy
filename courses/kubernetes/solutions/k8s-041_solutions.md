# k8s-041: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A recovery objective is a target, and a recovery measurement is an observation. Recovery Time Objective, or RTO, sets an acceptable duration for restoring the defined service. Recovery Point Objective, or RPO, sets an acceptable data-loss window. A drill must define start, finish and data reference points before it can compare observations with those objectives.

For this synthetic drill, interruption begins at 12:00:00Z. The application and independently restored marker both pass at 12:01:30Z, giving90 seconds of observed recovery time. The source's last durable marker was timestamped11:59:50Z, while the latest restored durable marker is11:59:30Z, giving a 20-second loss boundary under this example's timestamp assumptions. With targets120 seconds and30 seconds, these observed measures meet the two targets.

These calculations do not establish database transaction consistency or prove that no record outside the markers was lost. The immutable marker fixture makes a narrow data contract measurable. A Ready Pod at 12:00:40Z is an intermediate milestone, not the finish when the marker and ordinary service path are still unverified.

## Exercise 1: Define start and finish

The duration has meaning only relative to its milestones. Changing start from failure to detection after the drill can make the reported recovery seem faster without changing the system behavior, so definitions must remain explicit.

**Expected:** A fixed start definition and application+data finish predicate.

## Exercise 2: Compute observed recovery time

The elapsed time includes all required restoration and verification work in this definition. A Pod-ready milestone at 40 seconds is useful diagnostic detail but cannot substitute for the later complete acceptance time.

**Expected:** 90 seconds, compared with target 120 seconds.

## Exercise 3: Compute the data-loss boundary

This metric describes the represented marker timeline. It does not infer record counts or transactional consistency. The report must state how each timestamp relates to durable application data.

**Expected:** 20 seconds, compared with target 30 seconds.

## Exercise 4: Run the missing-step negative

The negative control catches a runbook that prematurely records success. It is especially important because a responding application can be serving empty, old or incorrect data while looking operationally healthy.

**Expected:** Recovery finish remains false.

## Exercise 5: Review clocks and evidence

The evidence packet should allow another person to recompute the result and understand uncertainty. Missing clock synchronization or ambiguous durability definitions should be reported rather than hidden behind precise-looking numbers.

**Expected:** Every measurement is traceable without exporting sensitive backup contents.

## Exercise 6: Write the objective conclusion

A useful conclusion explains whether the stated objective was met under the tested conditions and what prevented broader claims. It also records cleanup and any retained synthetic backup material so the drill is operationally complete.

**Expected:** A bounded drill conclusion with no universal recovery guarantee.

## Boundary and troubleshooting review

Meeting an objective once is a useful rehearsal result, not a guarantee that every future incident will recover within the same duration. Report the tested fault, data size, environment and operator procedure. Repeatability and broader failure coverage require additional independent drills.

Do not export private backups or credentials to make the evidence packet self-contained. The packet can include synthetic marker hashes, timestamps, operation receipts and protected backup references while leaving sensitive payloads under the host's access and retention policy.
