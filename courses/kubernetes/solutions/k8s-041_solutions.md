# k8s-041: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A recovery objective is a target, and a recovery measurement is an observation. Recovery Time Objective, or RTO, sets an acceptable duration for restoring the defined service. Recovery Point Objective, or RPO, sets an acceptable data-loss window. A drill must define start, finish and data reference points before it can compare observations with those objectives.

For this synthetic drill, interruption begins at 12:00:00Z. The application and independently restored marker both pass at 12:01:30Z, giving 90 seconds of observed recovery time. The source's last durable marker was timestamped 11:59:50Z, while the latest restored durable marker is 11:59:30Z, giving a 20-second loss boundary under this example's timestamp assumptions. With targets 120 seconds and 30 seconds, these observed measures meet the two targets.

These calculations do not establish database transaction consistency or prove that no record outside the markers was lost. The immutable marker fixture makes a narrow data contract measurable. A Ready Pod at 12:00:40Z is an intermediate milestone, not the finish when the marker and ordinary service path are still unverified.

## Exercise 1: Define start and finish

The duration has meaning only relative to its milestones. Changing start from failure to detection after the drill can make the reported recovery seem faster without changing the system behavior, so definitions must remain explicit.

**Expected:** A fixed start definition and application+data finish predicate.

**Solution reasoning**

- **Approach:** Write the start event and a finish predicate with both an application and a data check before reading the timeline.
- **Why it is correct:** Defining endpoints first prevents choosing them after seeing which gives the best number.
- **Plausible wrong approach:** Ending recovery when Pods are Ready ignores whether the data is correct.
- **How to verify:** Both definitions exist before the timeline is read, and finish includes application and data.

## Exercise 2: Compute observed recovery time

The elapsed time includes all required restoration and verification work in this definition. A Pod-ready milestone at 40 seconds is useful diagnostic detail but cannot substitute for the later complete acceptance time.

**Expected:** 90 seconds, compared with target 120 seconds.

**Solution reasoning**

- **Approach:** Subtract 12:00:00Z from 12:01:30Z in seconds.
- **Why it is correct:** One minute and thirty seconds is 90 seconds, which meets the 120 second target.
- **Plausible wrong approach:** Using a local timezone for one value and UTC for the other shifts the result by hours.
- **How to verify:** The answer is 90 seconds against a 120 second target.

## Exercise 3: Compute the data-loss boundary

This metric describes the represented marker timeline. It does not infer record counts or transactional consistency. The report must state how each timestamp relates to durable application data.

**Expected:** 20 seconds, compared with target 30 seconds.

**Solution reasoning**

- **Approach:** Subtract restored point 11:59:30Z from source point 11:59:50Z.
- **Why it is correct:** Twenty seconds of writes are missing, which is within the 30 second recovery point objective.
- **Plausible wrong approach:** Subtracting from the interruption time measures something other than lost data.
- **How to verify:** The answer is 20 seconds against a 30 second target.

## Exercise 4: Run the missing-step negative

The negative control catches a runbook that prematurely records success. It is especially important because a responding application can be serving empty, old or incorrect data while looking operationally healthy.

**Expected:** Recovery finish remains false.

**Solution reasoning**

- **Approach:** Evaluate service_ok AND data_ok AND Pod_ready.
- **Why it is correct:** With data_ok false, the AND is false regardless of the other inputs.
- **Plausible wrong approach:** Counting two of three as mostly recovered replaces the predicate with a vote.
- **How to verify:** Finish evaluates to false.

## Exercise 5: Review clocks and evidence

The evidence packet should allow another person to recompute the result and understand uncertainty. Missing clock synchronization or ambiguous durability definitions should be reported rather than hidden behind precise-looking numbers.

**Expected:** Every measurement is traceable without exporting sensitive backup contents.

**Solution reasoning**

- **Approach:** For each milestone, record clock source, timezone, backup reference, marker hash and host receipt.
- **Why it is correct:** Durations are only valid if both timestamps come from comparable clocks and each milestone points to its evidence.
- **Plausible wrong approach:** Mixing a learner laptop clock with a host clock adds unknown skew to the result.
- **How to verify:** Each milestone names its clock source and timezone, and no backup contents are exported.

## Exercise 6: Write the objective conclusion

A useful conclusion explains whether the stated objective was met under the tested conditions and what prevented broader claims. It also records cleanup and any retained synthetic backup material so the drill is operationally complete.

**Expected:** A bounded drill conclusion with no universal recovery guarantee.

**Solution reasoning**

- **Approach:** Report target, observed value, failed controls and untested conditions.
- **Why it is correct:** A drill shows one result under its conditions, and the failed data gate must stay visible.
- **Plausible wrong approach:** Writing that recovery meets objectives omits the failed check and the untested scenarios.
- **How to verify:** All four items appear, and there is no universal recovery guarantee.

## Boundary and troubleshooting review

Meeting an objective once is a useful rehearsal result, not a guarantee that every future incident will recover within the same duration. Report the tested fault, data size, environment and operator procedure. Repeatability and broader failure coverage require additional independent drills.

Do not export private backups or credentials to make the evidence packet self-contained. The packet can include synthetic marker hashes, timestamps, operation receipts and protected backup references while leaving sensitive payloads under the host's access and retention policy.
