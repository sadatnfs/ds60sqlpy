# Go curriculum guidance

Read the repository AGENTS.md, content contract and add-learning-path skill.
This subject owns courses/go only. Preserve stable go-001 through go-048 IDs
and saved-work identity. The registered language and runtime profile are go;
the ordinary pad is one main.go in the Linux Docker worker with CGO disabled.

Durable content lives in authoring/foundations.py, composition.py and systems.py.
authoring/render.py derives the route, manifest, guides, answer-free starters,
complete reference programs and explanatory solutions. Run authoring/build.py
after changing those sources. The renderer requires gofmt, so a contributor must
prepare Go explicitly. Shared make generate does not replace this step.

Each lesson has six distinct cases with an input/task, expected observation,
executable assertion and explanation. The first two appear as worked examples.
Preserve the separation of starter, guide, reference and explanatory solutions.
Keep math explicitly delimited and fences tagged. Do not use em dashes.

Ordinary examples must remain deterministic, bounded and offline after image
preparation. Do not add client-go, database drivers, cgo or live endpoints to
a standard-library reference without coordinating a reviewed runtime change.
The prepared client-go fixture is a separate real dependency project with an
explicit target contract. Models for Kubernetes, transactions and leader
election must state what they do not establish. Never turn a fake test into a
claim of cluster acceptance. Treat resourceVersion as opaque, preserve exact
UID ownership and never use ambient kubeconfig.

Check every changed reference with the actual declared worker when available.
Local Go runs are additional evidence, not Linux-container acceptance. Preserve
meaningful error and boundary cases and do not weaken checks to get a green run.
Use grouped parallel repository tests and keep all learner state untouched.

Use [the subject authoring guide](authoring/README.md) for regeneration and
[the module contract](../../docs/implementation/ADDING_A_MODULE.md) for shared
runtime integration. Root guidance owns common formatting, saved-work and
publication rules; subject changes must preserve those boundaries.
