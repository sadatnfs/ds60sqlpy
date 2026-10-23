# Studying PyTorch and TensorFlow together

Learn the mathematical contract first: input and target shapes, scalar loss,
reduction convention, trainable state and expected gradient. Then compare the
framework implementations under the same fixed numerical fixture. Matching
function names are less useful than matching those contracts.

| Question | PyTorch route | TensorFlow route |
| --- | --- | --- |
| Where are parameters registered? | nn.Module parameters and buffers | Keras layers and tracked variables |
| How is a gradient requested? | requires_grad, backward or autograd.grad | GradientTape and gradient |
| When do gradients accumulate? | Leaf .grad state unless cleared | Explicit returned gradients and update logic |
| How does training mode change behavior? | module.train()/eval(), separate grad mode | training argument and GradientTape scope |
| How does a batch reach the model? | Dataset, DataLoader, collation | tf.data and explicit model input |
| What survives restart? | Model, optimizer, RNG and data-position contract | Model/optimizer/checkpoint and data-position contract |
| What is an inference artifact? | State contract or supported export program | Keras model or SavedModel endpoint contract |

Each row requires concrete evidence. For example, switching to eval mode does
not itself disable PyTorch autograd. A TensorFlow inference endpoint can depend
on resource variables owned by a loaded object. Tensor layouts and loss
reductions can differ even when forward outputs look plausible. The paired
lessons expose these differences with small values and deliberate failures.

Keep framework-specific workflows idiomatic. A successful CPU toy experiment
does not prove GPU throughput, distributed scaling or production reliability.
Advanced chapters explain how to design those additional measurements and
which setup is separate from the default offline classroom.
