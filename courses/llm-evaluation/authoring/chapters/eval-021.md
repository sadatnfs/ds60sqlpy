## Keep the three policies and states distinct

PPO collects trajectories using an old policy and then optimizes a surrogate using those stored actions and log probabilities. The old policy is a snapshot of the collector. A separate reference policy may define a KL regularization target. The current policy changes during optimization. Confusing these roles changes the ratios and the learning problem.

A value function estimates expected future return under a declared policy and discount. A rollout with \(T\) steps needs \(T\) rewards and terminal flags plus \(T+1\) value estimates, including the final bootstrap value. Both discount and trace factors are in \([0,1]\). For reward \(r_t\), value estimate \(V(s_t)\), discount \(\gamma\) and a true terminal indicator \(d_t\), the temporal residual is

\[
\delta_t=r_t+\gamma(1-d_t)V(s_{t+1})-V(s_t).
\]

Generalized advantage estimation combines residuals using a trace factor \(\lambda\). In the finite rollout below, work backwards with \(\widehat A_t=\delta_t+\gamma\lambda(1-d_t)\widehat A_{t+1}\). A true terminal state removes bootstrapping. A rollout cut short by a time limit may still need the final value estimate. A separate episode boundary must also stop a trace from leaking into a new episode.

## Worked case A: terminal versus truncated trajectories

The authored two-step trajectory has rewards 1 and 2, values 0.5,0.4,0.2, gamma 0.9 and lambda 0.8. With a true final terminal, its advantages are 2.012 and 1.6. Treating the final step as a truncated continuation uses the final value and changes them to 2.1416 and 1.78. The helper accepts one contiguous rollout; it does not concatenate unrelated episodes.

{{WORKED_A}}

## Worked case B: clipping depends on the advantage sign

For a collected action, the probability ratio is \(\rho_t=\pi_\theta(a_t\mid s_t)/\pi_{\mathrm{old}}(a_t\mid s_t)\). PPO's clipped maximization term is

\[
\min\left(\rho_t\widehat A_t,
\operatorname{clip}(\rho_t,1-\epsilon,1+\epsilon)\widehat A_t\right).
\]

With positive advantage, the favorable increase is clipped above the upper ratio boundary. With negative advantage, the favorable decrease is clipped below the lower boundary. A bad-direction change can still be penalized outside the interval. Multiplying a clipped ratio by advantage without taking the minimum is not the same objective.

{{WORKED_B}}

## What clipping does not guarantee

The surrogate is not a hard constraint that every probability ratio stays within the interval. An optimizer step can overshoot a boundary, and parameters shared across actions can move unobserved actions. The reference constructs two valid policies with the same probability for the one observed action but very different probabilities elsewhere. Their sampled clipped terms agree while their full KL divergences differ.

Monitor actual divergence, entropy, clipping frequency, value error and task reward rather than assuming the clipping parameter supplies a universal trust-region guarantee. Old log probabilities and computed advantages should be treated as fixed data during the policy update. Allowing gradients through the old snapshot or an unintended value baseline changes the optimization.

## Connect to language-model training

Autoregressive responses are trajectories with a declared stopping rule. A final response-level reward can be distributed through value estimates and temporal advantages, while token masks determine which positions contribute. Variable lengths, padding, truncation and rewards assigned at intermediate steps require careful accounting. A copied generic PPO loop without these contracts is not a complete language-model training implementation.

The code demonstrates exact advantage arithmetic and surrogate behavior on small arrays. It does not collect language-model rollouts. The next unit performs actual PyTorch updates on a finite contextual policy, keeping the limitations explicit. The comparison with an independently evaluated utility remains necessary even when the optimizer and gradients are correct.
