# C++ guide depth authoring

Run `python courses/cpp/authoring/depth/build_depth.py` from the repository root with the standard-library Python runtime. It updates the 38 added guides and explanatory solutions from explicit topic-specific inputs, embeds the 76 complete worked programs and preserves the original four pilot lesson bodies. It never edits learner pads, compiles code, installs tools or starts Docker.

program_inputs.json contains complete example definitions and bodies. build_programs.py selects explicit standard headers and writes examples/. expected_outputs.json is an independently recorded output oracle from actual compiler executions; the generator does not recompute expected answers. details04_14.py, details15_28.py and details29_42.py hold mechanisms and debugging explanations. normalize_prose.py changes only prose spacing outside code/link contracts.

The depth command is idempotent against the authored base guides. It replaces marked explanation regions and the two worked-example sections, leaving six-task contracts, capstone host-project handoffs and executable official references intact. Do not rerun historical scratch reference generators to apply a prose change. The existing parser/cancellation references include separately reviewed corrections.

The Docker-only project instructions are retained in docker-projects.md.in. Update this input and compile-and-run.md together if their commands change. The multifile fixture now has genuine local install/export targets. Actual image/CMake execution belongs to the integration owner; native example tests are a separate evidence row.

Validation: tests/test_cpp_worked_examples.py compiles and executes all 76 programs, checks guide/source/output parity, tests the NDEBUG branch and inspects the documented Docker project/install contract. tests/test_systems_complete.py retains independent official-reference, mutation, linker and capstone checks. The guide examples do not reveal the six official exercise answers automatically.

## Shared maintenance gates

Use [CONTRIBUTING](../../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.
