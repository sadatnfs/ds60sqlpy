# Java completion andexecution checkpoint

Updated2026-10-23. All36 reviewed IDs, `java-001` through `java-036`, are authored andregistered. Stable IDs andprerequisites are preserved. Each bundle has a standalone guide,two complete worked Main.java examples,six exercise contracts,an answer-free learner source,a separate executable reference andan explanatory solution. Guide word counts range from1436 to2176.

## Actual subject coverage

The route includes language/type/object fundamentals,collections andgenerics,closures/streams,timezones andDST,owned filesystem work,Optional/error contracts,tests with meaningful mutants,search/sorting/DP,thread happens-before andlost updates,executor timeout/cancellation/backpressure,locks andatomics,Java21 virtual threads,reachability,module/classpath boundaries,reproducible JARs,loopbackHTTP,realH2/JDBC transactions,strict versioned binary serialization,ServiceLoader,JFR,application boundaries,ports/adapters,a tested local data service andrelease integrity checks.

JDBC29 requires the prepared `/opt/course-libs/h2-2.5.252.jar`. It uses real `java.sql` operations against unique `jdbc:h2:mem:` fixtures,with bound parameters,commit/rollback,constraint failures andtwo-session READ_COMMITTED visibility. It doesnot simulate a database orcontact shared infrastructure. The serialization encoder anddecoder reject malformed UTF-8 andbounded-length violations. HTTP fixtures bind only127.0.0.1 andclose owned listeners.

## Source andmanual fixtures

Portable authoring sources are in `courses/java/authoring/`. Regenerate with:

```text
python courses/java/authoring/build.py
```

Manual source trees andcommands for026,027 and036 are in `courses/java/fixtures/`. Tests verify that these source files exactly match the literal programs compiled by the single-file references. Optional jlink image creation remains a manual,unexecuted path;tool presence is not reported as a built-runtime receipt. All generated learner work belongs under ignored learner-owned directories,not source or anephemeral browser pad.

## Focused validation

```text
python -m pytest tests/test_java_lessons.py -q --disable-warnings
```

Host result: **4 passed, 36 skipped**. The skips are opt-in actual JDK execution cases. Structural checks cover all36 paths,prerequisites,minimum teaching depth,six exercises,solution separation,Main.java contracts,no em dashes,manual-source parity andreal JDBC boundaries.

All 36 Java references now have successful actual Java21/H2 Linux arm64 Docker evidence. The first 12 passed in `work/java-lessons-acceptance.jsonl`, 013-020 in `work/java-intermediate-acceptance.jsonl`, and 13 of 021-036 in `work/java-advanced-acceptance.jsonl`. Repaired 026, 027 and 036 passed in `work/java-packaging-repaired-acceptance.jsonl`.

Those three repairs preserve inherited JVM environment constraints and capture child stdout and stderr separately. The image's JAVA_TOOL_OPTIONS diagnostic is valid stderr, not part of an application's exact stdout contract. The release negative case checks stderr deliberately. Guide, learner, reference and portable specifications agree. The JDBC lesson uses the actual pinned H2 driver and passed in the same prepared image. Optional jlink image creation remains unexecuted.

## Remaining work

The JavaScript/TypeScript route and the substantive ML content quality pass remain active. Root owns shared runtime, Compose, navigation and whole-product delivery. No Git commit, push, engine change or package installation was performed by this content workstream.
