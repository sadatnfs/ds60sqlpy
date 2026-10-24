# docker-017: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

An architecture is a machine instruction family such as amd64 or arm64. A Linux image can target one or several architectures. A multi-platform image index points to platform-specific images; it is not one binary that magically runs everywhere. The engine selects a compatible image based on platform metadata.

An Apple Silicon laptop commonly runs arm64 natively while many hosted runners use amd64. Emulation can run some foreign-architecture programs, but it adds cost and does not prove native performance or compatibility. A successful source build on one platform is only evidence for that platform’s produced artifact.

Cross-compilation and emulation are distinct strategies. A compiler may emit target binaries while itself running natively; an emulator executes foreign instructions. Some projects need target-specific libraries or test hosts. A release matrix must name which platforms were actually built and executed.

BuildKit exposes platform arguments such as BUILDPLATFORM and TARGETPLATFORM. A Dockerfile may choose a native builder stage and pass the target into a compiler. Do not use these names as a substitute for correct compiler flags. A multi-platform build also needs an output strategy compatible with your image store or a deliberate export.

The course does not push images. For an optional local experiment, build one selected platform with `--load` when supported and inspect the result. Do not force a foreign platform on the ordinary classroom just to avoid investigating a missing dependency wheel.

## Exercise 1: Predict whether Linux implies amd64.

Linux supports multiple instruction families. A release statement should name both dimensions rather than collapsing them into a single platform label.

**Expected:** No; operating system and architecture are separate axes.

## Exercise 2: Classify cross-compilation and emulation.

A cross-compiler can be native while its output is foreign. Emulation may permit execution but changes performance and cannot establish all native behavior.

**Expected:** Producing target code versus executing foreign code.

## Exercise 3: Design a two-platform evidence matrix.

Do not fill an execution cell from an index manifest alone. The matrix should make untested combinations visible.

**Expected:** Separate build and execution columns for amd64 and arm64.

## Exercise 4: Diagnose exec format error.

A program can fail before its entry point because the kernel cannot load its format. Changing business logic or increasing memory will not fix that boundary.

**Expected:** Inspect architecture and executable format before app logic.

## Exercise 5: Explain why multi-platform output is not always one --load result.

Understand the selected build driver and local store rather than assuming every multi-platform result can be loaded identically on every engine.

**Expected:** Exporter and image-store capabilities constrain output.

## Exercise 6: Write an honest portability claim.

Source portability is valuable but weaker than observed execution. Architecture-specific dependencies and runtime behavior need their own evidence.

**Expected:** Name the tested platform and label other platforms unqualified.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
