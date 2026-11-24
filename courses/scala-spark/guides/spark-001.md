# spark-001: Choose a Scala-first or PySpark-first local route

Authored classroom lesson. Content availability and runtime readiness are separate checks. Read the current capability notice before running. Opening or saving this lesson does not install tools, start a cluster or prove mastery.

## Level and prerequisites

Beginner; 45 minutes. Direct prerequisites: none. Use the subject browser to open prerequisite lessons or review their concepts. Runtime readiness is checked separately before execution.

Learner artifact: [spark-001.md](../lessons/spark-001.md). Keep [solutions](../solutions/spark-001_solutions.md) closed until an attempt or explicit reveal.

## Learning objectives

- Explain the JVM, Scala binary version, Python driver, Spark engine, and the difference between a proposed profile and an available runner.
- Produce the exact bounded evidence named by the six exercises and explain one counterexample.

## Vocabulary and concepts

A source file is a description of work. A compiler checks Scala syntax and produces JVM bytecode; a JVM executes that bytecode. Spark is a separate data engine. PySpark lets a Python driver describe work that the Spark engine evaluates. Having Python alone does not establish a Spark installation. A version report is evidence about installed tools; a candidate compatibility tuple is a design choice until a real profile executes.

The Scala-first route needs no Python prerequisite. The PySpark-first route
uses existing Python functions, collections and testing skills, represented by
`python-10`. Both routes eventually need the same row and schema concepts.
The classroom's configured Spark image uses Spark 4.0.1 and the Scala 2.13
binary line with Java 17, while its worker Python is 3.12. Consult the actual
worker version report and the [versioned Spark requirements](https://spark.apache.org/docs/4.0.1/)
when reproducing a run. A compatible version range is useful setup guidance;
it is separate from evidence that your current worker executed successfully.

- **JDK:** the development kit including compiler/runtime tools for Java bytecode
- **JVM:** the process executing compatible bytecode
- **binary line:** a compatibility family such as Scala 2.13, reflected by artifact suffix _2.13
- **driver:** the program coordinating a Spark application
- **`local[2]`:** a local Spark master using two worker threads, not two remote computers

## Worked example / walkthrough

### Worked example 1: Trace a Scala program

The arrows are different phases. A source edit does not retroactively modify a process that already ran.

```text
Main.scala -> Scala compiler -> Main.class -> JVM process -> stdout: 42
```

The source file is the only thing you edit. A minimal version looks like this:

```scala
object Main {
  def main(args: Array[String]): Unit = {
    println(40 + 2)
  }
}
```

```text
$ scalac Main.scala   # writes Main.class
$ scala Main          # starts a JVM process
42
```

**Expected:** The editable input is Main.scala; 42 is an observation from the process.

### Worked example 2: Distinguish a candidate from a receipt

A supported version range cannot prove that dependencies were downloaded, matched or executed on this machine. The following deliberately hypothetical report illustrates that distinction; it is not a report of your running classroom.

```text
candidate: Spark 4.2.0 / Scala 2.13.18 / JDK 21
receipt: profile absent; no executed probe
```

A receipt only exists after a probe actually runs. This small program would produce one, because every printed value comes from the running driver rather than from a planning document:

```scala
import org.apache.spark.sql.SparkSession

object VersionProbe {
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder().master("local[2]").appName("version-probe").getOrCreate()
    try {
      println(s"spark=${spark.version}")
      println(s"scala=${scala.util.Properties.versionNumberString}")
      println(s"java=${System.getProperty("java.version")}")
    } finally spark.stop()
  }
}
```

Until that program has been compiled and executed on the machine in question, the report above stays a candidate.

**Expected:** Compatibility-informed, execution not established.

## Exercises

### Exercise 1: Trace artifacts

Label each artifact and explain what can be edited.

**Inputs/evidence:** Main.scala, Main.class, stdout 42 and exit 0.

**Expected result/shape:** Source, compiled bytecode, observed output and process status are four different categories.

**Verify:** Label all four; do not call stdout a source file.

**Progressive hints:**

1. Start with the human-editable file.
2. A compiler produces a new artifact.
3. Output is evidence after a process runs.

### Exercise 2: Select a language entry

Choose a route for two learners: no programming background, and tested Python skills.

**Inputs/evidence:** Learner A has no prior language; B can write functions and pytest tests.

**Expected result/shape:** A takes spark-002 to spark-010; B takes spark-011 after a python-10 competency check; both enter spark-012.

**Verify:** Name both routes and explain why Scala-first needs no Python.

**Progressive hints:**

1. Prior knowledge changes the entry point.
2. Do not require both languages before beginning.
3. Scala spark-010 OR Python bridge spark-011 establishes readiness for spark-012.

### Exercise 3: Check the binary suffix

Review dependency labels before any download.

**Inputs/evidence:** `spark-sql_2.13` at 4.2.0 versus a proposed `spark-sql_3` substitution.

**Expected result/shape:** Retain the documented Scala 2.13 line; reject the unsupported Scala 3 substitution for this profile.

**Verify:** Cite the binary suffix and actual profile receipt separately.

**Progressive hints:**

1. Find the suffix after the underscore.
2. Distinguish language patch from binary family.
3. The selected Spark artifact must match the compiler/runtime family.

### Exercise 4: Read capability truthfully

Classify candidate, missing and verified readiness.

**Inputs/evidence:** Candidate tuple; absent image; executed probe with digest and versions.

**Expected result/shape:** `candidate=proposed`, `absent=unavailable`, executed matching `receipt=qualified` only for its tested platform.

**Verify:** Write all three labels without inventing an execution.

**Progressive hints:**

1. What actually ran?
2. Separate configuration from observation.
3. A receipt names exact versions and platform.

### Exercise 5: Reject an unintended target

Compare local mode with a remote master.

**Inputs/evidence:** `local[2]` and `spark://shared.example:7077`.

**Expected result/shape:** Only the bounded local profile is eligible for this lesson; the remote master is outside its scope.

**Verify:** Identify the remote address and keep the saved attempt without connecting.

**Progressive hints:**

1. Read the master string.
2. A remote hostname changes the resource boundary.
3. Keep `local[2]` and refuse ambient remote settings.

### Exercise 6: Transfer a version report

Explain a report that has Python but no JVM.

**Inputs/evidence:** Python 3.12 present; java unavailable; Spark profile absent.

**Expected result/shape:** Ordinary Python may run, but Scala/Spark is unavailable; no installation occurs on Run.

**Verify:** Name the missing layer and preserve your route/prediction notes.

**Progressive hints:**

1. Python is one layer.
2. Which process runs Spark work?
3. Request profile preparation rather than claiming readiness.

## Self-check

- Can you reproduce each exact observation without reading the official answer?
- Can you explain a failed check using the lesson's model, rather than changing an expected value?

## Retrieval and transfer

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

## Common pitfalls

Do not confuse Scala 3 with the selected Scala 2.13 Spark binary family. Do not treat a proposed tuple or an exit 0 from another program as a Spark qualification receipt. Never route this lesson to an ambient remote master.

## Next step

Continue with [spark-002](spark-002.md) for Scala-first study, or use the authored [PySpark bridge, spark-011](spark-011.md) when its Python prerequisites are familiar. See the [course README](../README.md) for how these routes meet.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach spark-001.
Read courses/scala-spark/guides/spark-001.md and courses/scala-spark/lessons/spark-001.md.
Direct prerequisites: none. This lesson is authored; check its current runtime readiness and direct prerequisites.
Explain one mechanism, ask me to predict, let me attempt one exercise, then give one hint at a time.
Do not read courses/scala-spark/solutions/ until I make an honest attempt or explicitly ask for a reveal.
Review my exact values, diagnostics or written evidence; distinguish source inspection, process success and verified understanding.
Finish with a changed fixture and retrieval in my own words. Do not install tools, download assets or select an ambient cluster for me.
```
