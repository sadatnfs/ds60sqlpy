# tf-007: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/tf-007.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](tf-007_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

## Exercise 1: Trace a recorded path

The subtraction w-2 and the square of that result occur inside GradientTape, so the tape records their dependence on the trainable Variable. At zero the loss is 4 and the derivative is -4. The input dtype is float64 and CPU placement is explicit. A tape is an operational recording scope, not a symbolic parser that searches later Python text for a weight name. Its result should agree with the scalar derivative already checked in the previous lessons.

**Expected:** Loss 4 and gradient -4 at \(w=0\), dtype float64.

**Verify:** Assert the scalar values and inspect that subtraction and square both occur inside the tape indentation.

## Exercise 2: Distinguish a true zero

At \(w=2\) the same recorded path still exists. Its residual is zero and the connected derivative is the numeric tensor zero. Check that the result is not None before inspecting its scalar value. The distinction matters because a legitimate stationary point should not be diagnosed as a broken recording, and a broken recording should not be disguised as a stationary point. The fixture isolates this mechanism without asserting that every zero gradient in a larger network indicates an optimum.

**Expected:** Connected loss 0 and numeric gradient 0, not None.

**Verify:** Use is not None before comparing the gradient value to 0.

## Exercise 3: Repair a missing path

Computing square(w-2) before entering the tape creates an eager value without recording the Variable-dependent path in that tape. Copying that value inside the scope does not repair the missing earlier operations, so the gradient is None. Recompute the subtraction and square inside a fresh scope to obtain -4. Retain the two outcomes together; replacing a missing gradient with zero would let the update appear to run while hiding the reason no parameter connection was observed.

**Expected:** Outside path gives None; repaired path at zero gives -4.

**Verify:** Retain both results and assert their different types/values rather than converting None to zero.

## Exercise 4: Watch a constant deliberately

A trainable Variable is normally watched automatically when read, while a constant is not. Explicitly tape.watch(c) tells TensorFlow to record differentiation with respect to a floating constant used in the subsequent computation. It gives -4 here; the unwatched case is None. A fixed feature x can remain constant while another parameter w has a derivative through operations involving x. Trainability and mathematical dependence are related but distinct contracts.

**Expected:** Unwatched constant gives None; explicitly watched constant gives -4.

**Verify:** Assert both outcomes and explain why this does not make all input features trainable parameters.

## Exercise 5: Preserve Variable identity

The expression \(w-0.1\cdot \mathrm{gradient}\) creates a Tensor. Assigning that result to a Python name rebinds the name and leaves the original Variable unchanged at zero. By contrast, assign_sub mutates the existing Variable, preserving its identity and bringing its value to 0.4. Retain a reference to the original object when comparing the two cases so a renamed Tensor cannot masquerade as mutable parameter state. Identity becomes important when optimizers track state for particular parameter objects.

**Expected:** Rebinding yields a Tensor at 0.4 while the old Variable remains 0; assign_sub preserves the Variable object and changes its value to 0.4.

**Verify:** Inspect isinstance(...,tf.Variable), object identity and both old/new numeric values.

## Exercise 6: Use a fresh recording

An ordinary nonpersistent tape releases its recorded resources after one gradient query; a second query raises RuntimeError. Build a new tape and recompute the forward loss to ask again. The scalar derivative is still -4. For fixed \(x=2\) and \(\mathrm{loss}={\left(2\cdot w-4\right)}^{2}\) at zero, the chain rule gives \(2\cdot (-4)\cdot 2=-16\). This confirms that a feature can remain constant while the weight has a connected gradient. No persistent tape or trainable feature is necessary for the example.

**Expected:** Second use of the consumed tape raises RuntimeError; a fresh scalar tape gives -4, and the constant-feature loss gives gradient -16.

**Verify:** Capture the consumed-tape exception and assert the two fresh-path gradients separately.

## Inspectable reference functions

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

```python
from __future__ import annotations
import math
import tensorflow as tf


def gradient_at(value):
    with tf.device("/CPU:0"):
        weight = tf.Variable(value, dtype=tf.float64)
        with tf.GradientTape() as tape:
            loss = tf.square(weight - 2.0)
        gradient = tape.gradient(loss, weight)
    if gradient is None:
        raise ValueError("recorded scalar path is disconnected")
    return float(loss.numpy()), float(gradient.numpy())
```

## Retrieval and alternatives

Close the examples and explain the three different observations None, numeric zero and RuntimeError after tape consumption. Then derive the gradient of \({\left(3\cdot w-6\right)}^{2}\) at zero before running a fresh recording.

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.
