# cuda-110: Custom operator packaging and binary portability

**Route:** CUDA Python and machine learning. **Stage:** advanced. **Prerequisites:** `cuda-061`, `cuda-097`, `cuda-098`.

Pacing, evidence labels and platform rules: [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

- List compatibility axes.
- Separate import and execution.
- Explain native code versus intermediate code.
- Design a build ledger.
- Test unsupported dtype.
- Define a package release gate.

## Mechanism and vocabulary

A native extension package combines Python compatibility, framework ABI, host compiler, CUDA toolkit, architecture targets and system libraries. A wheel filename alone does not promise every GPU can execute its embedded code. Native device binaries target architectures; intermediate representations can provide a JIT path only within supported compatibility rules. Record what was built and what was actually executed.

Use a fixed project with reviewed build dependencies and reproducible metadata. Test import, operator registration, forward/backward behavior and unsupported-input failure in each declared environment. Keep build-time downloads explicit and separate from classroom reading. The browser's single-file pad does not become a general package manager. Publishing packages or using external registries is a separately authorized workflow.



### Key terms

- **Framework ABI:** The binary interface of a framework build that a native extension must match.
- **Wheel:** A built Python package whose tags describe Python and platform compatibility but not every GPU it can run on.
- **Native cubin:** Compiled device code for a specific GPU architecture that runs without just-in-time compilation.
- **PTX:** An intermediate representation that the driver can JIT-compile for newer architectures within compatibility rules.
- **Build ledger:** A record of compiler, toolkit, framework, architecture targets and what was actually executed.

## Worked examples

### Worked example 1

A package can import because its host shared library loads, then fail when the first kernel lacks compatible device code. Import is only the first qualification step.

### Worked example 2

Two environments with the same Python version but different framework ABI or CUDA assumptions may need separate builds. Preserve a matrix rather than claiming universal portability.

## How to run the CPU model

Edit the copy; the [reference](../references/cuda-110_cpu.py) adds assertions.

```sh
python courses/cuda/python/lessons/cuda-110_cpu.py
```

```python
required = {"python", "framework", "toolkit", "host_arch", "device_targets"}
manifest = {
    "python": "pinned",
    "framework": "pinned",
    "toolkit": "pinned",
    "host_arch": "declared",
    "device_targets": ["qualified separately"],
}
assert set(manifest) == required
assert "driver" not in manifest
print("CPU package ledger: build metadata complete; runtime driver still separate")
```

**Expected observation:** Build ledger completeness does not establish runtime driver or GPU acceptance.

## Practice and transfer

Record each attempt in the [worksheet](../lessons/cuda-110.md) before opening hints.

### Exercise 1: List compatibility axes

**Trap to avoid:** Recording only the Python version suggests one wheel works everywhere that Python runs, while a framework ABI change alone can break the import.

### Exercise 2: Separate import and execution

**Trap to avoid:** Treating a successful import as proof of portability passes packages that cannot run any kernel on the target GPU.

### Exercise 3: Explain native code versus intermediate code

**Trap to avoid:** Shipping native code only for the build machine's GPU makes the package fail on any older or newer architecture.

### Exercise 4: Design a build ledger

**Trap to avoid:** Building from a developer machine without recording flags yields an artifact nobody can reproduce or audit.

### Exercise 5: Test unsupported dtype

**Trap to avoid:** Silently casting to float32 hides precision loss and gives callers a different result from what they requested.

### Exercise 6: Define a package release gate

**Trap to avoid:** Testing one environment and declaring the whole matrix supported presents untested claims as verified.

## Progressive hints

Hint *k* belongs to exercise *k*; open one at a time.

1. List every axis a native extension depends on, from the Python version to the driver on the host.
2. Ask what loads when the package imports and what is only exercised when the first kernel actually runs.
3. Compare code compiled for specific GPU architectures with intermediate code that a driver can compile later.
4. Write what a reviewer needs to rebuild the same artifact: input versions, hashes and compiler flags.
5. Call the operator with a dtype it does not support and describe the error the user should see.
6. For each environment you claim to support, list the tests that must pass before release.

## Common mistakes and self-check

A common mistake is treating a successful import as proof that the package works on a machine. The host shared library can load while the first kernel fails because the wheel has no compatible device code for that GPU. Another mistake is claiming universal portability from one build; two environments with the same Python version but a different framework ABI or CUDA assumption may need separate builds. Fix both by maintaining a tested compatibility matrix and running import, registration, forward, backward and unsupported-input tests in every declared environment.

**Misconception:** Embedding PTX in a wheel means the operator will run on every current and future GPU. **Correction:** The driver can compile intermediate PTX at load time only within compatibility rules. The driver must understand that PTX version, and PTX targets a minimum architecture, so it can run on that architecture and newer ones but not on older ones. Just-in-time compilation also adds a first-launch delay that depends on the installed driver. Record which native architectures and PTX targets the build contains, test the first kernel launch on each declared GPU and mark untested devices as untested.

**Evidence limit:** The reference checks that a build ledger is complete. A complete ledger does not show that a driver accepts the binaries or that a GPU runs the kernels; that requires executing real kernel work in each declared environment, which this lesson cannot do on a classroom worker.

1. Why does a wheel filename not guarantee GPU support?
2. When can intermediate device code help portability?
3. Is publishing a package part of this lesson's workflow?

Answers: [self-check answers](../solutions/cuda-110_solutions.md#self-check-answers).

## Primary references

- [PyTorch CUDA semantics](https://docs.pytorch.org/docs/2.9/notes/cuda.html)
- [TensorFlow GPU guide](https://www.tensorflow.org/guide/gpu)

Full lists: [documentation and sources](../../STUDY-GUIDE.md#documentation-and-sources).

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for cuda-110: Custom operator packaging and binary portability.
Read courses/cuda/python/guides/cuda-110.md and courses/cuda/python/lessons/cuda-110.md.
Start with my current attempt and the two worked examples, and ask which backend actually ran.
Give one progressive hint at a time. Keep the separate solution closed and do not mark
progress unless I request it. Treat synthetic timings and CPU models as model evidence,
not as GPU or cluster measurements.
```
