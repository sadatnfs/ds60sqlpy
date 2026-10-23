# Java: from the first compile to reliable applications

All36 lessons in the [reviewed route](track.json) now have complete authored bundles in the [manifest](lessons.json). The course starts with source,types,control flow andobjects,then develops collections,generics,functional code,testing,algorithms,concurrency,files,HTTP,JDBC,serialization,service discovery,profiling andrelease engineering. Every guide has two complete worked examples,six inspectable exercises,mechanism explanations,diagnosis,hints andseparate executable/explanatory solutions.

Use the Docker classroom's prepared Java21 profile. The pad is compiled as `Main.java` with `--release 21` andrun with assertions enabled. Helper classes can share that file. You do not need a host JDK. Source viewing,compilation,reference execution andlearner mastery are separate evidence;the [checkpoint](../../docs/implementation/java-content-status.md) records actual prepared-container results.

## Runtime andresource boundaries

Default examples use small local fixtures andprepared JDK libraries. JDBC29 additionally uses the pinned H2 driver already included in the Java image at `/opt/course-libs/h2-2.5.252.jar`. It opens only owned in-memory H2 databases andperforms real SQL/transaction checks. No lesson installs a package orcontacts a shared database.

HTTP lessons start short-lived loopback servers on ephemeral ports andclose them after checks. Concurrency lessons use bounded waits andcooperative cleanup. Module,JAR,JFR andrelease examples write only owned temporary files. The [manual module fixture](fixtures/java-026/README.md), [manual JAR fixture](fixtures/java-027/README.md) and [optional jlink workflow](fixtures/java-036/README.md) explain multi-file orlarger packaging work outside the single-file pad. A customruntime image is platform-specific andis not claimed built by the default reference.

Keep attempts in saved classroom pads oryour own ignored `.learning/` copy. Do not edit official solutions to obtain a passing run. Predict outputs andfailure types,attempt the exercises,then compare with the reference andsolve a fresh boundary case.

| Lesson | Topic |
| --- | --- |
| [java-001](guides/java-001.md) | From source file to running JVM |
| [java-002](guides/java-002.md) | Values, numeric types and conversion |
| [java-003](guides/java-003.md) | Decisions, loops and invariants |
| [java-004](guides/java-004.md) | Methods and explicit contracts |
| [java-005](guides/java-005.md) | Arrays, strings and Unicode |
| [java-006](guides/java-006.md) | Lists, sets and maps |
| [java-007](guides/java-007.md) | Classes and encapsulation |
| [java-008](guides/java-008.md) | Constructors, records and invariants |
| [java-009](guides/java-009.md) | Exceptions and resource lifetime |
| [java-010](guides/java-010.md) | Interfaces and polymorphism |
| [java-011](guides/java-011.md) | Equality, hashing and ordering |
| [java-012](guides/java-012.md) | Generics and variance |
| [java-013](guides/java-013.md) | Lambdas and functional interfaces |
| [java-014](guides/java-014.md) | Streams and collectors |
| [java-015](guides/java-015.md) | Dates, time zones and formatting |
| [java-016](guides/java-016.md) | Files, paths and character encoding |
| [java-017](guides/java-017.md) | Optional values and validation boundaries |
| [java-018](guides/java-018.md) | Tests that detect broken behavior |
| [java-019](guides/java-019.md) | Data structures and complexity |
| [java-020](guides/java-020.md) | Search, sorting and dynamic programming |
| [java-021](guides/java-021.md) | Threads and the memory model |
| [java-022](guides/java-022.md) | Executors, futures and cancellation |
| [java-023](guides/java-023.md) | Locks, atomics and concurrent collections |
| [java-024](guides/java-024.md) | Virtual threads and blocking work |
| [java-025](guides/java-025.md) | JVM memory, GC and allocation |
| [java-026](guides/java-026.md) | Packages, classpaths and modules |
| [java-027](guides/java-027.md) | Builds and dependency reproducibility |
| [java-028](guides/java-028.md) | HTTP services and clients |
| [java-029](guides/java-029.md) | JDBC and transactions |
| [java-030](guides/java-030.md) | Serialization and schema evolution |
| [java-031](guides/java-031.md) | Reflection, annotations and service loading |
| [java-032](guides/java-032.md) | Profiling and benchmark reasoning |
| [java-033](guides/java-033.md) | Secure application boundaries |
| [java-034](guides/java-034.md) | Application design and dependency boundaries |
| [java-035](guides/java-035.md) | Build a tested local data service |
| [java-036](guides/java-036.md) | Package, diagnose and maintain a release |

## Evidence andnext work

The references include actual compiler diagnostics,controlled lost updates,executor cancellation andqueue rejection,virtual-thread admission limits,module resolution,fresh-JVM JAR launch,prepared JDBC transactions,JFR readback andnegative integrity gates. Their bounded fixtures do not establish production service reliability,cross-platform installer acceptance oruniversal performance claims.

Use the [Docker classroom guide](../../docs/docker-classroom.md) for image preparation,visible logs,persistent learner state andstopping the environment. The course's full quality review also checks explanation depth,assumptions andfailure analysis beyond minimum word orartifact counts.
