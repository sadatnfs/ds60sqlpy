# tf-032: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Saving has two distinct purposes: preserving a trainable Keras model and exporting an inference interface. The .keras format preserves a Keras model configuration and state; model.export creates an inference artifact that can be loaded through SavedModel. Keras3 does not use model.save(directory) as the export workflow. Prediction parity must be checked after reconstruction, ideally in a fresh process. Matching predictions says nothing about whether optimizer state can resume the same next update, which is the separate checkpoint lesson. This fixture has one fixed weight and a known signature, so failures can be attributed to persistence and interface behavior rather than training randomness.

**Serialization:** Encoding model configuration and state into a recoverable artifact.

**Export:** Publishing a fixed inference interface and its state.

**Parity:** Agreement of outputs under declared inputs and tolerance.

## Reading the implementation

Save the built model to a path ending.keras. Load it with tf.keras.models.load_model. Export to a different owned directory and load it with tf.saved_model.load; call its serve endpoint. TemporaryDirectory owns both outputs. The child process accepts only the two local artifact paths created by the parent and prints predictions as JSON. Compare using float32 tolerance1e-6.

## Exercise 1: Create a fixed inference model

The question is: Set a bias-free Dense weight to2 and predict on 1,3.

A known fixed weight avoids making serialization success depend on a stochastic training result. The input shape and dtype are part of the inference contract.

```python
model = tf.keras.Sequential(
    [
        tf.keras.Input(shape=(1,)),
        tf.keras.layers.Dense(
            1, use_bias=False, kernel_initializer=tf.keras.initializers.Constant(2.0)
        ),
    ]
)
x = np.array([[1.0], [3.0]], dtype="float32")
expected = model(x).numpy()
np.testing.assert_array_equal(expected, [[2], [6]])
```

**Expected:** predictions2,6.

**Verify:** Compare the computed values or written argument with predictions2,6.

## Exercise 2: Round-trip .keras

The question is: Save and reload the model in a temporary directory.

Reconstruction must use the saved artifact rather than another reference to the original model object. File existence alone does not establish that deserialization works.

```python
temporary = tempfile.TemporaryDirectory()
folder = Path(temporary.name)
keras_path = folder / "model.keras"
model.save(keras_path)
loaded = tf.keras.models.load_model(keras_path)
np.testing.assert_allclose(loaded(x).numpy(), expected, atol=1e-6, rtol=0)
```

**Expected:** reloaded predictions match within 1e-6.

**Verify:** Compare the computed values or written argument with reloaded predictions match within 1e-6.

## Exercise 3: Export an inference endpoint

The question is: Call model.export into a different temporary subdirectory and load SavedModel.

The export exposes inference behavior. Treating it as interchangeable with a resumable training object would overstate what the endpoint contains.

```python
export_path = folder / "inference"
model.export(export_path)
exported = tf.saved_model.load(str(export_path))
np.testing.assert_allclose(exported.serve(tf.constant(x)).numpy(), expected, atol=1e-6, rtol=0)
```

**Expected:** serve returns the same predictions.

**Verify:** Compare the computed values or written argument with serve returns the same predictions.

## Exercise 4: Check both in a fresh process

The question is: Load the .keras model and exported endpoint in a child interpreter and compare their outputs.

The child cannot reuse live model state from the parent. Keep the object returned by tf.saved_model.load in a named variable while calling serve: the exported function references resource variables owned by that object. Chaining load(...).serve(...) can let the owner disappear before its variables are used. Prediction parity therefore depends on both reconstructed state and correct object lifetime, not only a readable file.

```python
program = textwrap.dedent("""
import json,sys,tensorflow as tf
x=tf.constant([[1.],[3.]])
a=tf.keras.models.load_model(sys.argv[1])(x).numpy().tolist()
exported=tf.saved_model.load(sys.argv[2])
b=exported.serve(x).numpy().tolist()
print(json.dumps([a,b]))
""")
compile(program, "checkpoint-child", "exec")
result = subprocess.run(
    [sys.executable, "-c", program, str(keras_path), str(export_path)],
    capture_output=True,
    text=True,
    check=False,
    timeout=60,
)
if result.returncode:
    raise RuntimeError("child process failed: " + result.stderr)
a, b = json.loads(result.stdout.strip().splitlines()[-1])
np.testing.assert_allclose(a, expected, atol=1e-6, rtol=0)
np.testing.assert_allclose(b, expected, atol=1e-6, rtol=0)
```

**Expected:** both child outputs[[2],[6]].

**Verify:** Compare the computed values or written argument with both child outputs[[2],[6]].

## Exercise 5: Check a new batch length

The question is: Use three valid rows instead of two with the restored model.

The feature width stays fixed while batch length varies. This confirms the intended leading-axis flexibility, not support for arbitrary feature dimensions.

```python
new = loaded(np.array([[0.0], [2.0], [4.0]], dtype="float32")).numpy()
assert new.shape == (3, 1)
np.testing.assert_array_equal(new[:, 0], [0, 4, 8])
```

**Expected:** output shape(3,1), predictions0,4,8.

**Verify:** Compare the computed values or written argument with output shape(3,1), predictions0,4,8.

## Exercise 6: Remove only owned artifacts

The question is: Clean the temporary directory and check both artifacts are absent.

The example has no persistent model output by design. A real release should choose an explicit learner-owned artifact destination and retain a rollback version instead.

```python
temporary.cleanup()
assert not folder.exists()
```

**Expected:** temporary directory absent.

**Verify:** Compare the computed values or written argument with temporary directory absent.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
