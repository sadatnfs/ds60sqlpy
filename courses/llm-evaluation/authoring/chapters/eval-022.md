## A small real optimization experiment

This unit performs actual PyTorch forward, backward and optimizer steps. The policy has two contexts and two actions per context. Its trainable logits form a2-by -2 table, and its critic has one value per context. The environment terminates after one action, so returns equal immediate rewards and no temporal trace is needed. This isolates PPO's objective from the GAE boundary issues studied previously.

The rollout distribution is enumerated exactly. Both contexts have probability one half, and each action is weighted by the frozen old policy's probability. This computes the surrogate expectation without sampling noise. It is not a claim that a real language-model action space can be enumerated, nor a simulation of token generation. The advantage of the reduction is that every weight, reward and update can be inspected.

At the start of each outer iteration, the code copies the current policy probabilities into a detached old snapshot. It then makes three optimizer steps against that snapshot. The reference policy remains uniform throughout training and supplies a separate KL penalty. Those two distributions serve different purposes even when they happen to match at initialization.

## Worked case A: improve the declared task reward

The useful action is 0 in the first context and 1 in the second. Starting from uniform action probabilities gives expected reward one half. The reference implementation updates the actor with the clipped PPO term and the critic with a weighted squared-error loss. It recomputes final expected reward after all updates and checks improvement beyond 0.9 on this exact finite task.

{{WORKED_A}}

## Worked case B: correct optimization of an incorrect reward

The second fit reverses the reward table while retaining the same independent task utility. Its training reward improves, but true task utility becomes poor. The implementation is doing what its objective requests. This is a concrete connection to reward-model shortcuts: a trustworthy gradient does not guarantee a trustworthy target.

{{WORKED_B}}

## Follow the computational graph

The old probabilities are detached from the graph. The advantages also use detached value estimates. Actor gradients therefore do not secretly change the baseline or the old distribution to improve the ratio expression. The critic has its own regression term. These choices are tested directly in the reference rather than inferred from a successful loss curve.

For a one-step context, the critic's target is the immediate action reward under the old policy weighting. It estimates an expected return, not the maximum possible reward. As the actor changes, the distribution underlying that expectation changes too. An accurate value estimate for a previous policy can therefore become stale without a software defect.

The program logs state-level action probabilities and final reward. A larger training system should additionally retain rollout identity, masks, objective coefficients, clipping frequency, gradient behavior and actual KL to the old and reference policies. Objective components have different units and reductions; their coefficients are not transferable merely because another project uses the same optimizer.

## Transfer to sequence models carefully

A language-model policy uses conditional token distributions along sampled histories. Its data pipeline must distinguish prompt tokens, generated tokens, padding, truncation and true stopping. Rollout collection, advantage estimation, reference log probabilities and held-out evaluation become separate substantial components. The finite example verifies none of their model-serving or accelerator properties.

Use this exercise to understand and diagnose the optimization mechanism before adopting a larger implementation. Keep a separate evaluation corpus, task utility and critical-policy checks. A new reward or prompt can change the data-generating process, so a previous successful optimization run is not evidence that the modified assistant will behave acceptably.
