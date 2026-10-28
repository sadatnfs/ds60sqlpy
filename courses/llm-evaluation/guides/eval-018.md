# eval-018: Train and audit a small reward model

## Starting point and outcome

Advanced; approximately 120 minutes. Direct prerequisites: `eval-017`, `torch-004`.

Perform actual CPU gradient updates on a tiny reward predictor and expose a length shortcut using independent comparison features.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-018`, and use its `llm-torch-cpu` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

## What this model learns

This unit trains an actual PyTorch linear reward model with three input features: correctness evidence, citation evidence and a length feature. The features are authored numbers, not outputs from a language encoder. The model has three learned weights and no bias because a shared bias would cancel in a pairwise score difference. It is a small mechanism experiment, not a pretrained language model or an empirical study of human preferences.

For a pair of feature vectors, the model receives their difference \(d_i=f(x,a)-f(x,b)\). Its logit is \(w^{\mathsf T}d_i\). Binary cross entropy on that logit corresponds to the Bradley-Terry likelihood from the previous unit. Soft labels of one half are used here as an explicit convention for authored tie examples. They do not claim to model every kind of indifference.

The loss adds a small squared-weight penalty. This controls the scale of a separable fit and makes the finite training problem more stable. The reported loss belongs to the final recomputed weights, not to the pre-update state from the last loop iteration. Every fit starts from zero weights, uses float64 arithmetic and a fixed number of CPU steps.

## Worked case A: a length-balanced training design

The first training set includes positive correctness and citation comparisons plus symmetric length-only ties. The length coordinate therefore receives no systematic preference signal. After optimization, a held-out response with better correctness and citation evidence remains preferred even when it is shorter by three units. The code verifies actual loss reduction, the near-zero length coefficient and the sign of the held-out margin.

```python
import torch

torch.set_num_threads(1)
DTYPE = torch.float64


def fit_reward(differences, labels, steps=160):
    x = torch.tensor(differences, dtype=DTYPE)
    y = torch.tensor(labels, dtype=DTYPE)
    model = torch.nn.Linear(3, 1, bias=False, dtype=DTYPE)
    with torch.no_grad():
        model.weight.zero_()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.3)

    def objective():
        return (
            torch.nn.functional.binary_cross_entropy_with_logits(model(x).squeeze(-1), y)
            + 0.01 * model.weight.square().sum()
        )

    initial = float(objective().detach())
    for _ in range(steps):
        optimizer.zero_grad()
        loss = objective()
        loss.backward()
        optimizer.step()
    final = float(objective().detach())
    return model, initial, final


def worked_a():
    x = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, -1]]
    y = [1, 1, 0.5, 0.5]
    model, initial, final = fit_reward(x, y)
    probe = torch.tensor([[1.0, 1.0, -3.0]], dtype=DTYPE)
    assert final < initial and final < 0.5
    assert abs(float(model.weight[0, 2].detach())) < 1e-12
    assert float(model(probe).detach()) > 2
    print("Balanced fit loss:", initial, final, "held-out margin:", float(model(probe).detach()))


worked_a()
```

## Worked case B: a shortcut can fit training and fail transfer

The second design always pairs preferred examples with greater length. It contains no length-balanced counterexamples. Optimization can reduce training loss by assigning a large positive coefficient to length. A held-out comparison reverses that correlation while retaining the intended evidence advantages; the learned preference then reverses incorrectly.

```python
import torch

torch.set_num_threads(1)
DTYPE = torch.float64


def fit_reward(differences, labels, steps=160):
    x = torch.tensor(differences, dtype=DTYPE)
    y = torch.tensor(labels, dtype=DTYPE)
    model = torch.nn.Linear(3, 1, bias=False, dtype=DTYPE)
    with torch.no_grad():
        model.weight.zero_()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.3)

    def objective():
        return (
            torch.nn.functional.binary_cross_entropy_with_logits(model(x).squeeze(-1), y)
            + 0.01 * model.weight.square().sum()
        )

    initial = float(objective().detach())
    for _ in range(steps):
        optimizer.zero_grad()
        loss = objective()
        loss.backward()
        optimizer.step()
    final = float(objective().detach())
    return model, initial, final


def worked_b():
    model, initial, final = fit_reward([[1, 0, 3], [0, 1, 3]], [1, 1])
    probe = torch.tensor([[1.0, 1.0, -3.0]], dtype=DTYPE)
    assert final < initial and float(model(probe).detach()) < 0
    assert float(model.weight[0, 2].detach()) > float(model.weight[0, 0].detach())
    print("Shortcut fit loss:", initial, final, "held-out margin:", float(model(probe).detach()))


worked_b()
```

## Read the gradient before trusting a training curve

At zero weights, every predicted probability is one half. The unregularized gradient is \(D^{\mathsf T}(0.5-y)/n\). The reference compares this expression to autograd on a fresh model. Agreement supports the implemented objective and shape convention; it does not validate the feature design or labels.

The optimizer changes parameters because those parameters reduce the chosen objective. It has no independent knowledge that length is an undesirable shortcut. Improving a training loss can therefore accompany worse held-out preference behavior. Keep the held-out comparison definition separate from the training criterion and preserve its original features and labels.

## Diagnosis and model governance

Inspect coefficients, errors and sensitivity tests before a policy optimizer consumes the reward. A linear model makes those weights easy to inspect, but a deeper reward model needs analogous interventions and validation rather than a claim that its hidden representation must be better. Check performance across prompts, answer lengths, task families and annotation conditions.

Regularization is a modeling choice, not a cure for omitted counterexamples. More iterations on the biased comparison set do not create the missing evidence. Add appropriate comparison coverage, revise the feature/label design and assess the changed procedure on new held-out cases.

## Scope of the computation

The code performs real forward passes, backward passes and optimizer steps. It downloads no data or parameters and uses no accelerator. The generated records demonstrate a particular shortcut under known construction. They do not prove that all real judges prefer long responses or that any deployed reward model has the same defect. The next units use explicit finite policies to study how optimizing an imperfect reward can amplify this kind of failure.


## Six investigations

### 1. Verify the initial gradient

Compare autograd at zero weights with \(D^{\mathsf T}(0.5-y)/n\).

**Expected:** The two vectors match in float64.

**Hint:** Use pairwise feature differences as rows.

### 2. Inspect the length coefficient

Train the balanced design in case A.

**Expected:** The length coefficient remains approximately zero.

**Hint:** Its two tie comparisons are symmetric.

### 3. Reverse a comparison

Negate the held-out feature difference.

**Expected:** The linear reward margin changes sign.

**Hint:** There is no bias term.

### 4. Find a training shortcut

Inspect the weights from case B.

**Expected:** Length receives more weight than either evidence coordinate.

**Hint:** The biased design makes length strongly predictive of labels.

### 5. Recompute the final loss

Evaluate the objective after the final optimizer step.

**Expected:** The final-state loss is distinct from the last pre-update loss.

**Hint:** Logging order is part of the artifact identity.

### 6. State the model boundary

Describe what the three learned weights establish.

**Expected:** A real small CPU reward fit, with no natural-language capability claim.

**Hint:** Identify the representation and its provenance.

## Primary references

- [PyTorch binary cross entropy with logits](https://docs.pytorch.org/docs/2.9/generated/torch.nn.BCEWithLogitsLoss.html)
- [Preference-based learning](https://arxiv.org/abs/1706.03741)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
