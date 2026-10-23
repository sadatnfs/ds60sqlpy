# Authoring Deep learning with TensorFlow and Keras

Follow root [AGENTS.md](../../AGENTS.md) and the
[lesson contract](../../docs/content-authoring.md). The design source is
[the reviewed track](../../docs/expansion/tracks/deep-learning-tensorflow.md).

- Preserve the reviewed stable IDs and prerequisites. `lessons.json` inventories
  authored artifacts for the module catalog; it does not alter the legacy
  catalog or enable a runtime by itself. Keep unfinished IDs absent instead of inventing placeholder bodies.
- Define every new term, explain the code or reasoning anatomy, give two focused
  worked examples, and supply six distinct exercises with exact Expected/Verify
  observations. Keep executable and explanatory solutions separate from learners.
- Use tiny literal local fixtures and explicit float tolerances. Pair predictions
  with their actual observations. A copied public test is rehearsal, not blind
  assessment; retain fresh retrieval and transfer evidence.
- The orientation worksheet uses reading mode and needs no job. All executable
  content is Python. NumPy is a declared dependency, not part of the standard
  library. TensorFlow or PyTorch execution requires a qualified runtime profile;
  an import, parser result or Dockerfile alone is not that qualification.
- Never install packages in lessons, fetch models/data, call a hosted service,
  use a GPU by default, or infer a runtime from an authored file. No database is
  involved. Keep CPU fixtures small enough for bounded worker execution.
- Leave learner state under `.learning/` alone. Reference code must not overwrite
  learner files or write models into this source tree. Verifier fixtures contain
  typed inputs/expected values, not shell commands or network targets.
- Keep source, guide, both solutions, metadata and tests aligned. Run the focused
  content tests and a real qualified-runtime probe when relevant. Report every
  unexecuted heavy-runtime surface explicitly.
- Do not use em dashes in authored content.
