## Hamiltonian dynamics uses gradients to move through a density

Hamiltonian Monte Carlo augments a position q with momentum p. Its potential energy is minus the log target density, and its kinetic energy depends on a positive-definite mass matrix. Hamiltonian dynamics can move through a high-dimensional distribution more efficiently than repeatedly guessing an unrelated local direction, but the numerical integration and geometry still matter.

For the one-dimensional standard-normal target with unit mass, \(U(q)=q^2/2\), \(K(p)=p^2/2\), and \(H(q,p)=U(q)+K(p)\). A leapfrog step updates momentum by a half gradient step, position by a full step, and momentum by another half step. Its symmetry and volume-preserving structure support a Metropolis correction for numerical integration error.

The program demonstrates the integrator only. It does not implement a complete HMC or NUTS inference engine, momentum-refresh policy, adaptation schedule or production diagnostic suite. The later prepared PyMC and Stan profiles perform actual library inference.

## Worked case 1: verify reversibility and energy behavior

Starting from position .5 and momentum .7, ten steps of size .2 produce a small energy error. Integrating again from the endpoint with reversed momentum returns the original position and the negative original momentum within numerical tolerance.

This reversibility calculation is an independent test of the half-step ordering. Omitting the final half update or using the wrong sign can break the property. The program also checks the Hamiltonian difference, which determines the acceptance correction when this integrator is embedded in an appropriate HMC transition.

In a full HMC method, momentum is sampled from its specified distribution, the numerical trajectory is generated, and a proposal is accepted with a probability involving the Hamiltonian change. Exact dynamics would preserve energy; finite steps usually do not. The correction is part of the algorithm, not evidence that arbitrarily inaccurate trajectories are efficient.

## Worked case 2: make the integrator unstable

The step size is increased to three for the same target and trajectory length. The energy error becomes enormous and the implied Metropolis acceptance probability is effectively zero. The exact model and initial state have not changed; the numerical method has.

A large step can miss important curvature or become unstable. A very small step can make integration accurate but require many gradient evaluations to travel a useful distance. The computational tradeoff is therefore about effective exploration per cost, not minimizing integration error in isolation.

Posterior geometry can vary across the parameter space. A step size suitable in a broad region may fail in a narrow funnel. Rescaling parameters, choosing a better metric or using a noncentered parameterization can change that geometry. A higher target acceptance is sometimes useful, but it is not a universal substitute for understanding the model.

## Relate the demonstration to NUTS

The No-U-Turn Sampler adaptively chooses trajectory lengths using a criterion intended to avoid retracing a path unnecessarily. It also operates within a careful transition construction; simply stopping an arbitrary integrator when a path looks circular is not an implementation of NUTS.

Prepared libraries report quantities such as divergences, tree depth, step size and energy diagnostics. A divergence is evidence that the numerical exploration encountered a problematic region under the configured algorithm. It should be investigated in relation to parameters and geometry, not automatically discarded as an inconvenient warning.

Mass-matrix terminology varies across interfaces. Some expose a metric or inverse mass rather than the mass itself. Record the convention before interpreting a fitted matrix. Confusing a covariance with its inverse can reverse an intended rescaling and make computation worse.

## Answered scientific discussion

**Does increasing the number of leapfrog steps fix an excessive step size?** Not generally. More unstable updates can amplify the numerical error. Step size and trajectory length affect different aspects of the transition.

**Why use an analytic normal target before a complex posterior?** Its gradient and Hamiltonian are known, so reversibility, signs and numerical behavior can be checked directly. Those checks establish the integrator mechanism; actual posterior inference also needs correct density code, adaptation and diagnostic evidence.
