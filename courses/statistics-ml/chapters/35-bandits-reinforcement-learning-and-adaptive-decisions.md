# 35. Bandits, Reinforcement Learning, and Adaptive Decisions

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-035`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Adaptive decisions differ from ordinary prediction because the chosen action changes both outcomes and the information observed next. A recommender learns mostly from items it exposes. A maintenance policy changes which failures are observed. A support assistant that chooses a tool can affect the state it is trying to understand. The central question is therefore which policy to follow while learning, subject to operational constraints and uncertainty.

### Bandits and long-horizon control

A bandit chooses an action and receives a reward without modeling a lasting state transition relevant to later decisions. A contextual bandit conditions that choice on observed context. A Markov decision process adds a state transition: today's action can change tomorrow's opportunities and rewards. If those consequences matter, optimizing immediate reward can be shortsighted. If they do not, a full reinforcement-learning system may add unnecessary complexity.

For policy pi, discounted return is G_t=sum_(k>=0) gamma^k R_(t+k+1), with discount factor gamma between zero and one in an infinite-horizon discounted formulation. Value V_pi(s) is the expected return starting in state s and following pi. The Bellman equation separates immediate reward from discounted next-state value. It is a consistency relation under the environment model, not a guarantee that a learned estimate is correct.

### Exploration buys information at a cost

Always choosing the current best estimated action can lock the system into an early mistake because rejected alternatives receive little new evidence. Randomized exploration, confidence bonuses and posterior sampling provide different ways to gather information. Their guarantees depend on stationarity, reward distributions, support and action constraints. An exploration action can affect real people or consume real resources, so the experiment must operate within the allowed action set and decision authority.

### Logged data do not identify every new policy

Offline policy evaluation compares a target policy with the behavior policy that generated data. Importance weights pi(a|x)/b(a|x) correct action-selection differences only where the behavior probability b is positive and credible. For trajectories, products of ratios can produce extreme variance. A model-based or doubly robust estimator adds outcome structure, but it cannot create direct evidence for actions never tried without extrapolation assumptions.

The same principle applies to agents built around language models. A high final-answer score does not excuse an unauthorized tool action, and a reward for finishing quickly can encourage skipping evidence. Define allowed actions and constraints outside the learned reward whenever they are mandatory. Evaluate trajectories, failures and recovery as well as final text.

### Diagnose before deploying adaptation

Specify the state and observation boundary, action set, reward timing, horizon, logging policy and constraints. Test a simple nonadaptive baseline and a small simulator whose limitations are explicit. Separate reward improvement in that simulator from evidence of real-world value. Use held-out logs or controlled experiments for policy evaluation, and preserve rollback and stopping rules. The worked examples show exact Bellman arithmetic, a Q update, importance weighting and a reward-hacking counterexample without running an online policy.

## Methods, mechanisms, and limits

### stat-35-01

**Multi-armed bandits**

Multi-armed bandits repeatedly choose among actions with uncertain reward distributions. The learner observes only the reward of the selected action, creating partial feedback. A classical stationary model assumes each action's distribution remains stable. This fits repeated short-term decisions better than actions with important delayed state effects. The action set, reward definition and exploration budget must be explicit before comparing algorithms.

### stat-35-02

**Exploration–exploitation tradeoffs**

The exploration-exploitation tradeoff balances immediate expected reward against learning that improves later choices. The value of information depends on remaining horizon and uncertainty, so a poorly known action is not automatically worth trying. Operational constraints can rule out otherwise informative actions. Evaluate cumulative reward and learning cost under the same horizon rather than celebrating fast convergence after ignoring early harmful decisions.

### stat-35-03

**Epsilon-greedy policies**

An epsilon-greedy policy chooses a random action with probability epsilon and an estimated-best action otherwise. It is simple and provides support when every action can be explored, but spreads exploration without considering which alternatives are most informative. A fixed epsilon keeps paying exploration cost indefinitely in a stationary environment. Decay schedules require assumptions about horizon and changing rewards.

### stat-35-04

**Upper confidence bound methods**

Upper confidence bound methods add an uncertainty bonus to estimated reward and choose the largest optimistic value. The bonus depends on observation counts and a reward/concentration model. This targets underexplored promising actions more deliberately than uniform random exploration. Misspecified bounds, heavy tails or nonstationarity can undermine guarantees; the displayed upper confidence value is conditional on the mathematical assumptions.

### stat-35-05

**Thompson sampling**

Thompson sampling draws a plausible reward model from a posterior and acts optimally under that draw. Repeated posterior sampling naturally balances uncertainty and estimated value. Priors and likelihoods determine what uncertainty means, and approximate inference can change behavior. A posterior is not automatically calibrated under model misspecification, so performance should be evaluated under plausible departures and operational constraints.

### stat-35-06

**Contextual bandits**

Contextual bandits choose actions based on observed features of the current situation, then observe a reward for the chosen action. They can personalize decisions while retaining a one-step reward focus. Contexts must be available before the action, and logged propensities are important for evaluation. If actions change future contexts in ways that matter, the contextual-bandit simplification may omit important long-term effects.

### stat-35-07

**Combinatorial bandits**

Combinatorial bandits choose a set or structured combination of actions, such as a slate of recommendations or a resource allocation. Feedback may reveal only the combined reward or component rewards, leading to different learning difficulty. The action space can grow exponentially, so optimization or approximation becomes part of the policy. Interactions among selected components invalidate a simple sum-of-independent-rewards assumption.

### stat-35-08

**Nonstationary bandits**

Nonstationary bandits allow reward distributions to change, using mechanisms such as sliding windows, discounting or change detection. Forgetting old data improves responsiveness but increases variance. Define a benchmark that can change at a plausible rate; comparison with a clairvoyant action changing every instant may be unattainable. Separate real reward shifts from changes in user mix or measurement.

### stat-35-09

**Regret analysis**

Regret is cumulative loss relative to a specified benchmark policy, often the best fixed action under a stationary bandit model. Dynamic regret uses a changing comparator and needs additional assumptions. Expected regret and realized reward differ, and constants can matter at operational sample sizes. A theoretical rate should not be interpreted as a guaranteed outcome on one finite run.

### stat-35-10

**Markov decision processes**

A Markov decision process specifies states, actions, transition probabilities, rewards and a horizon or discount. The Markov property means the state contains enough information for future dynamics given the action. A convenient feature vector may fail that property. Define terminal states and reward timing carefully, because an off-by-one transition or omitted state variable changes the control problem.

### stat-35-11

**Partially observable decision processes**

A partially observable process has hidden state observed through noisy or incomplete signals. A belief distribution over hidden states can serve as an information state when the model is known. Recurrent policies approximate history dependence but do not guarantee correct belief inference. Uncertainty about the environment and uncertainty about the current hidden state are distinct and may require different exploration or sensing actions.

### stat-35-12

**Bellman equations**

Bellman equations express value as expected immediate reward plus discounted value of the next state. Policy evaluation fixes the policy, while optimality equations maximize over actions. Solving them requires a valid model or suitable data-based estimates. A small residual in an approximate function class does not automatically bound decision error everywhere, especially in states poorly covered by training data.

### stat-35-13

**Dynamic programming**

Dynamic programming solves structured sequential problems by reusing values of subproblems, as in finite-horizon backward induction or policy/value iteration. It assumes access to transition and reward information in the standard model-based form. State-space size can make exact computation infeasible. Approximation errors must be considered when using reduced states or learned models.

### stat-35-14

**Q-learning**

Q-learning updates Q(s,a) toward r+gamma*max_a_prime Q(s_prime,a_prime) using a temporal-difference error. It is off-policy in its tabular formulation because the target uses a greedy next action while behavior may explore. Convergence needs appropriate conditions on visits and step sizes. Function approximation, bootstrapping and off-policy data can create instability beyond the simple tabular guarantee.

### stat-35-15

**Policy gradients**

Policy gradients optimize parameters of a stochastic policy using reward-weighted derivatives of log action probability. A baseline can reduce variance without changing the expected gradient when used appropriately. The sampled returns and advantage estimates determine variance and bias. A larger training return is not proof of safe or robust policy behavior, particularly when the reward proxy can be exploited.

### stat-35-16

**Actor–critic methods**

Actor-critic methods combine an actor policy with a critic estimating value or advantage. The critic can reduce gradient variance but introduces approximation error and coupled training dynamics. Bootstrapping and off-policy corrections need care. Monitor value estimation, policy entropy and actual task outcomes separately so a critic that becomes confidently wrong does not masquerade as policy improvement.

### stat-35-17

**Model-based reinforcement learning**

Model-based reinforcement learning plans using a known or learned transition/reward model. It can use data efficiently when the model captures relevant dynamics, but planning may exploit model errors in poorly observed regions. Short model rollouts, uncertainty penalties or real-data validation can limit this effect. Simulator success should be reported separately from real-environment acceptance.

### stat-35-18

**Offline reinforcement learning**

Offline reinforcement learning learns from a fixed interaction dataset without collecting new actions during training. The policy must avoid overestimating unsupported actions that look attractive under function approximation. Conservative objectives, behavior constraints and uncertainty methods address this challenge under different assumptions. Dataset coverage is central: a large log can still contain little evidence for the actions a proposed policy wants to take.

### stat-35-19

**Importance-sampling policy evaluation**

Importance-sampling evaluation reweights logged rewards by target-policy probability divided by behavior-policy probability. For trajectories the ratios multiply over time, often causing high variance. Support and correct propensities are essential. Clipping or self-normalization can stabilize estimates but change bias or estimand properties, so report those choices rather than hiding them inside an evaluation helper.

### stat-35-20

**Doubly robust policy evaluation**

Doubly robust policy evaluation combines a reward/value model with propensity-weighted residual corrections. Under suitable assumptions it can retain consistency if one nuisance component is correct, but sequential settings require careful definitions and regularity. Both components can fail in the same unsupported region. Cross-fitting and diagnostics reduce some overfitting issues without eliminating the need for action coverage.

### stat-35-21

**Constrained reinforcement learning**

Constrained reinforcement learning optimizes reward subject to limits on costs, risk or resource use. Expected cumulative constraints differ from per-step or high-probability guarantees. A penalty in the reward may encourage compliance without guaranteeing a mandatory boundary. Define feasibility and enforcement separately, and evaluate constraint violations under uncertainty rather than reporting reward alone.

### stat-35-22

**Reward design**

Reward design maps the actual operational goal into a measurable training signal. Immediate engagement, completion speed or textual preference may be convenient but incomplete proxies. Include delayed consequences and specify how competing objectives are handled. Mandatory permissions and safety boundaries should not depend solely on a learned scalar reward. Review whether optimizing the proxy can change the meaning of the data collected later.

### stat-35-23

**Reward hacking**

Reward hacking occurs when a policy improves the measured reward while failing the intended objective, such as producing persuasive unsupported answers for a judge that rewards style. The failure can arise without malicious intent from the optimizer. Use adversarial examples, independent outcome checks and constraint enforcement to expose proxy exploitation. A higher reward curve is therefore a diagnostic input, not final proof of task success.

## Worked Python demonstrations

Complete offline program: [chapter_35.py](../examples/chapter_35.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_35.py
```

### Separate a Bellman value from one learning update

A two-step deterministic path earns one now and two next, with discount 0.9, so its value is 1+0.9*2=2.8. A Q estimate initially zero with learning rate one-half moves only to 1.4 after one update toward that target. The value equation and the finite learning procedure are different objects.

### Correct a logging-policy mixture

The log contains equally probable actions zero and one, with rewards zero and one. Its raw reward mean is one-half. A target policy always choosing action one gives weights [0,2,0,2], and the weighted estimate is one. This exact balanced fixture illustrates the ratio; real finite samples need variance analysis and credible propensity logging.

### Expose a reward proxy that selects the wrong behavior

Action one has proxy score 0.99 but actual utility 0.1, while action zero has proxy 0.6 and utility 0.7. Maximizing the proxy chooses the worse action. In a language assistant, analogous behavior could be a verbose unsupported answer that pleases a weak judge. An independent utility check is therefore necessary.

### Complete executable example

```python
import numpy as np

def bellman_and_q():
    terminal=0.;v_second=2.+.9*terminal;v_first=1.+.9*v_second
    assert np.isclose(v_first,2.8)
    old_q=0.;alpha=.5;target=1.+.9*2.
    updated=old_q+alpha*(target-old_q)
    assert np.isclose(updated,1.4)
    print("Two-step value:",v_first,"one Q update:",updated)

def importance_weighting():
    action=np.array([0,1,0,1]);reward=np.array([0.,1.,0.,1.])
    behavior=np.full(4,.5);target=(action==1).astype(float)
    weights=target/behavior;estimate=np.mean(weights*reward)
    assert weights.tolist()==[0.,2.,0.,2.] and estimate==1.
    assert np.all(behavior>0)
    print("Logged mean:",reward.mean(),"target-policy estimate:",estimate)

def reward_proxy():
    proxy=np.array([.6,.99]);real_utility=np.array([.7,.1])
    selected=int(np.argmax(proxy));best=int(np.argmax(real_utility))
    assert selected==1 and best==0 and real_utility[selected]<real_utility[best]
    print("Proxy selects action",selected,"but true-utility best is",best)

def main():
    bellman_and_q();importance_weighting();reward_proxy()

if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: When is a bandit preferable to reinforcement learning?** When actions mainly affect immediate reward and do not materially change future state opportunities. The simpler problem can be easier to evaluate and control. If long-term consequences matter, document them rather than assuming a one-step approximation is harmless.

**Interview: Why is offline policy evaluation sometimes impossible?** If the logging policy never takes an action in a relevant context, observed data do not identify that action's reward without extra modeling assumptions. Importance weights cannot divide by zero support and create missing evidence.

**Interview: Does reward improvement establish agent reliability?** No. The policy may exploit a proxy, violate a constraint or fail under distribution shift. Evaluate actual task outcomes, allowed tool trajectories, failure handling and constraint adherence independently from the training reward.

## Primary sources and official APIs

- [Sutton and Barto, Reinforcement Learning: An Introduction, publisher page](https://mitpress.mit.edu/9780262039246/reinforcement-learning/)

- [Stanford CS234 lecture materials](https://web.stanford.edu/class/cs234/modules.html)

## Reading connections

[Previous chapter](34-generative-ai-and-language-model-evaluation.md) | [Book contents](../README.md) | [Next chapter](36-optimization-and-operations-research.md)
