# spark-001 learner worksheet

Authored classroom lesson. Content availability and runtime readiness are separate checks. Read the current capability notice before running. No opening or saving this lesson installs tools, starts a cluster or proves mastery.

Read the [guide](../guides/spark-001.md), predict first, and keep an independent response for each task. These are reasoning fixtures, not commands to execute.

## Worked example / walkthrough

### Worked example 1: Trace a Scala program

The arrows are different phases. A source edit does not retroactively modify a process that already ran.

```text
Main.scala -> Scala compiler -> Main.class -> JVM process -> stdout: 42
```

**Expected:** The editable input is Main.scala; 42 is an observation from the process.

### Worked example 2: Distinguish a candidate from a receipt

A supported version range cannot prove that dependencies were downloaded, matched or executed on this machine.

```text
candidate: Spark4.2.0 / Scala2.13.18 / JDK21
receipt: profile absent; no executed probe
```

**Expected:** Compatibility-informed, execution not established.

## Exercises

### Exercise 1: Trace artifacts

Label each artifact and explain what can be edited.

**Inputs/evidence:** For spark-001 Exercise 1, Main.scala, Main.class, stdout 42 and exit 0.

**Expected result/shape:** For spark-001 Exercise 1, source, compiled bytecode, observed output and process status are four different categories.

**Verify:** For spark-001 Exercise 1, label all four; do not call stdout a source file.

**Progressive hints:**

1. Start with the human-editable file.
2. A compiler produces a new artifact.
3. Output is evidence after a process runs.

### Exercise 2: Select a language entry

Choose a route for two learners: no programming background, and tested Python skills.

**Inputs/evidence:** For spark-001 Exercise 2, Learner A has no prior language; B can write functions and pytest tests.

**Expected result/shape:** For spark-001 Exercise 2, A takes spark002-010; B takes spark011 after a python-10 competency check; both enter spark012.

**Verify:** For spark-001 Exercise 2, name both routes and explain why Scala-first needs no Python.

**Progressive hints:**

1. Prior knowledge changes the entry point.
2. Do not require both languages before beginning.
3. Scala010 OR Python bridge011 establishes readiness for012.

### Exercise 3: Check the binary suffix

Review dependency labels before any download.

**Inputs/evidence:** For spark-001 Exercise 3, spark-sql_2.13 at4.2.0 versus a proposed spark-sql_3 substitution.

**Expected result/shape:** For spark-001 Exercise 3, retain the documented Scala2.13 line; reject the unsupported Scala3 substitution for this profile.

**Verify:** For spark-001 Exercise 3, cite the binary suffix and actual profile receipt separately.

**Progressive hints:**

1. Find the suffix after the underscore.
2. Distinguish language patch from binary family.
3. The selected Spark artifact must match the compiler/runtime family.

### Exercise 4: Read capability truthfully

Classify candidate, missing and verified readiness.

**Inputs/evidence:** For spark-001 Exercise 4, candidate tuple; absent image; executed probe with digest and versions.

**Expected result/shape:** For spark-001 Exercise 4, candidate=proposed, absent=unavailable, executed matching receipt=qualified only for its tested platform.

**Verify:** For spark-001 Exercise 4, write all three labels without inventing an execution.

**Progressive hints:**

1. What actually ran?
2. Separate configuration from observation.
3. A receipt names exact versions and platform.

### Exercise 5: Reject an unintended target

Compare local mode with a remote master.

**Inputs/evidence:** For spark-001 Exercise 5, local[2] and spark://shared.example:7077.

**Expected result/shape:** For spark-001 Exercise 5, only the bounded local profile is eligible for this lesson; the remote master is outside its scope.

**Verify:** For spark-001 Exercise 5, identify the remote address and keep the saved attempt without connecting.

**Progressive hints:**

1. Read the master string.
2. A remote hostname changes the resource boundary.
3. Keep local[2] and refuse ambient remote settings.

### Exercise 6: Transfer a version report

Explain a report that has Python but no JVM.

**Inputs/evidence:** For spark-001 Exercise 6, Python3.12 present; java unavailable; Spark profile absent.

**Expected result/shape:** For spark-001 Exercise 6, ordinary Python may run, but Scala/Spark is unavailable; no installation occurs on Run.

**Verify:** For spark-001 Exercise 6, name the missing layer and preserve your route/prediction notes.

**Progressive hints:**

1. Python is one layer.
2. Which process runs Spark work?
3. Request profile preparation rather than claiming readiness.

## My evidence

Record prediction, observation, explanation and one transfer result. Keep credentials and private machine paths out of your notes.
