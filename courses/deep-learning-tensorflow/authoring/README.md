# ML lesson authoring sources

These original topic specifications and renderer maintain the completed TensorFlow and LLM lesson bundles. They are authoring tools, not learner runtime dependencies. The existing first8 TensorFlow and first9 LLM lessons remain independently authored and are preserved.

Run from the repository root with a prepared Python interpreter:

```text
python courses/deep-learning-tensorflow/authoring/build.py
```

The renderer writes only the two ML course guides, learner worksheets, separate solutions and authored manifests. It does not change active catalog registration, runtime qualification, learner state or the shared practice registry. Each topic specification contains its own mechanism explanation, API anatomy, six concrete exercises, arithmetic expectations and explanatory solution code. After editing, run the focused ML tests and the relevant prepared runtime references.
