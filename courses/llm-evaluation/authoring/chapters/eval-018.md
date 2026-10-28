## What this model learns

This unit trains an actual PyTorch linear reward model with three input features: correctness evidence, citation evidence and a length feature. The features are authored numbers, not outputs from a language encoder. The model has three learned weights and no bias because a shared bias would cancel in a pairwise score difference. It is a small mechanism experiment, not a pretrained language model or an empirical study of human preferences.

For a pair of feature vectors, the model receives their difference \(d_i=f(x,a)-f(x,b)\). Its logit is \(w^{\mathsf T}d_i\). Binary cross entropy on that logit corresponds to the Bradley-Terry likelihood from the previous unit. Soft labels of one half are used here as an explicit convention for authored tie examples. They do not claim to model every kind of indifference.

The loss adds a small squared-weight penalty. This controls the scale of a separable fit and makes the finite training problem more stable. The reported loss belongs to the final recomputed weights, not to the pre-update state from the last loop iteration. Every fit starts from zero weights, uses float64 arithmetic and a fixed number of CPU steps.

## Worked case A: a length-balanced training design

The first training set includes positive correctness and citation comparisons plus symmetric length-only ties. The length coordinate therefore receives no systematic preference signal. After optimization, a held-out response with better correctness and citation evidence remains preferred even when it is shorter by three units. The code verifies actual loss reduction, the near-zero length coefficient and the sign of the held-out margin.

{{WORKED_A}}

## Worked case B: a shortcut can fit training and fail transfer

The second design always pairs preferred examples with greater length. It contains no length-balanced counterexamples. Optimization can reduce training loss by assigning a large positive coefficient to length. A held-out comparison reverses that correlation while retaining the intended evidence advantages; the learned preference then reverses incorrectly.

{{WORKED_B}}

## Read the gradient before trusting a training curve

At zero weights, every predicted probability is one half. The unregularized gradient is \(D^{\mathsf T}(0.5-y)/n\). The reference compares this expression to autograd on a fresh model. Agreement supports the implemented objective and shape convention; it does not validate the feature design or labels.

The optimizer changes parameters because those parameters reduce the chosen objective. It has no independent knowledge that length is an undesirable shortcut. Improving a training loss can therefore accompany worse held-out preference behavior. Keep the held-out comparison definition separate from the training criterion and preserve its original features and labels.

## Diagnosis and model governance

Inspect coefficients, errors and sensitivity tests before a policy optimizer consumes the reward. A linear model makes those weights easy to inspect, but a deeper reward model needs analogous interventions and validation rather than a claim that its hidden representation must be better. Check performance across prompts, answer lengths, task families and annotation conditions.

Regularization is a modeling choice, not a cure for omitted counterexamples. More iterations on the biased comparison set do not create the missing evidence. Add appropriate comparison coverage, revise the feature/label design and assess the changed procedure on new held-out cases.

## Scope of the computation

The code performs real forward passes, backward passes and optimizer steps. It downloads no data or parameters and uses no accelerator. The generated records demonstrate a particular shortcut under known construction. They do not prove that all real judges prefer long responses or that any deployed reward model has the same defect. The next units use explicit finite policies to study how optimizing an imperfect reward can amplify this kind of failure.
