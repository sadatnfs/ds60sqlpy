# Exact-version Catalyst project

This original teaching project compiles two expressions and one optimizer rule
against **Spark 4.0.1, Scala 2.13 and JDK 17**. Catalyst extension APIs have no
source or binary stability guarantee. It is a separately prepared multi-file
project, not an ordinary single-file classroom Run target.

The expression implements stable softplus for DOUBLE input, preserving nulls.
The rule removes a duplicate BIGINT nonnegative clamp. Its proof relies on
idempotence over exact long integers; it does not rewrite arbitrary floating
arithmetic. The probe checks generated/interpreted parity, extreme finite values,
nulls, invalid type/arity and the actual analyzed/optimized trees.

From the repository root, after preparing the ordinary Spark image:

```bash
docker run --rm --pull never --network none --memory 3g --cpus 2 \
  --read-only --tmpfs /tmp:rw,exec,size=536870912 \
  --mount "type=bind,src=$PWD/courses/advanced-spark-modeling/projects/catalyst,dst=/project,readonly" \
  --entrypoint python ds60sqlpy-worker-spark-local-scala:1.1.0 /project/run.py
```

Use the locally prepared version tag if different. No image is pulled by this
command. All classes, JARs and Spark scratch files live in disposable `/tmp`;
there is no learner volume and no Docker socket mount. A successful probe proves
this tiny single-host compiler/runtime contract, not production cluster speed.
Keep the exact image ID, source hashes and output when qualifying another build.

Read asm-021 through asm-023 for the lifecycle, code generation and rewrite proof.
The source is original; Apache Spark APIs are used under the project's ordinary
license. Consult the [versioned extension API](https://spark.apache.org/docs/4.0.1/api/scala/org/apache/spark/sql/SparkSessionExtensions.html).
