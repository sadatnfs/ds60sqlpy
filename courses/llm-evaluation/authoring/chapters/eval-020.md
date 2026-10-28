## Connect the preference model to a policy

The previous unit gives an exponential-tilt optimum for a KL-regularized finite policy. Rearranging that relation writes its reward as a reference-relative log probability plus a context-specific normalizing constant. A Bradley-Terry comparison subtracts the two rewards for the same context, so that shared constant cancels.

For a chosen response \(y_w\), rejected response \(y_l\), policy \(\pi_\theta\) and frozen reference \(\pi_{\mathrm{ref}}\), define

\[
m_\theta=\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}
-\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)},\qquad
\ell_{\mathrm{DPO}}=-\log\sigma(\beta m_\theta).
\]

This derivation depends on its preference and regularization assumptions. It does not mean that every preference dataset obeys them, or that a trained policy becomes a calibrated judge of factual correctness. DPO avoids a separately fitted reward predictor in this objective; it still uses response likelihoods, preference labels and a reference model.

## Worked case A: loss and derivative at the reference

When policy and reference coincide, the margin is zero and the loss is \(\log2\). For a two-action softmax, the policy log-odds difference is a single parameter. The code differentiates the loss with respect to that parameter and compares the analytic gradient to finite differences. With a positive preference and beta 2, the derivative at the reference is -1.

{{WORKED_A}}

## Worked case B: beta changes more than an initial step size

For three positive and one negative comparison of the same pair, the fitted classifier logit is \(\log3\). The policy log-odds shift is that value divided by beta. A larger beta can produce a larger initial gradient yet a smaller optimum shift for the same empirical preference frequency. This counterexample prevents the simplistic interpretation that increasing beta always pushes the learned policy further from the reference.

{{WORKED_B}}

## Sequence likelihoods and masks

A response log probability is a sum over its predicted tokens under the declared conditional histories. Prompt tokens used as conditioning are not necessarily part of the response loss. Padding and tokens after stopping must be excluded consistently, and the treatment of the end-of-sequence token must be stated. A length-normalized mean log probability defines a different objective from the sequence sum.

The reference includes a numerical counterexample where dividing chosen and rejected log ratios by their different lengths reverses the margin's sign. Neither calculation should be substituted for the other without changing the declared training objective. Keep tokenizer identity, masks, reference outputs and sequence lengths in the training artifact contract.

## Data and evaluation boundaries

Preference pairs may have been collected under a different policy. Their coverage and labeling process determine which comparisons the update sees. Missing response regions, annotator mixtures and presentation shortcuts remain relevant. A dataset of only unanimous wins can lead to a separable objective with no finite unconstrained optimum; regularization, early stopping or additional comparisons alter that situation.

Evaluate the resulting policy with independent task and critical-risk evidence. Do not use the same preferences both to choose hyperparameters and to make an untouched-final-set claim. A lower DPO loss demonstrates better fit to this objective, not necessarily a better assistant under an external task distribution.

This unit performs exact finite-action calculations. It does not fine-tune pretrained weights. The existing supervised adaptation route supplies real tiny decoder mechanics, while the next PPO units expose rollout policies, advantage estimation and actual small CPU policy updates under their own contracts.
