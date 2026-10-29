# TMB modeling with R and C++

Custom likelihoods, automatic differentiation, latent-variable integration and forecasting, with original R/C++ models and a separately prepared Python bridge.

This is a tutorial: complete examples and answered discussions are provided without exams. Begin with the R and C++ foundations listed by each chapter. The 48 base-R companions run offline in the prepared R runtime. Native TMB compilation and rpy2 are separately prepared project capabilities, not ordinary single-file R-pad operations.

## Chapters

1. [Why a C++ objective is called from R](guides/tmb-001.md)
2. [Template types and the objective contract](guides/tmb-002.md)
3. [The full Gaussian negative log likelihood](guides/tmb-003.md)
4. [Stable parameter constraints](guides/tmb-004.md)
5. [Compile, load and isolate an owned library](guides/tmb-005.md)
6. [MakeADFun values and gradients](guides/tmb-006.md)
7. [nlminb and optimization evidence](guides/tmb-007.md)
8. [Hessian, curvature and weak identification](guides/tmb-008.md)
9. [REPORT versus ADREPORT](guides/tmb-009.md)
10. [A nonlinear trend likelihood](guides/tmb-010.md)
11. [Count and censored likelihood terms](guides/tmb-011.md)
12. [Fixed effects and latent random effects](guides/tmb-012.md)
13. [Deriving the Laplace approximation](guides/tmb-013.md)
14. [Inner and outer convergence](guides/tmb-014.md)
15. [AR(1) states and sparse precision](guides/tmb-015.md)
16. [Independent panels and parameter ownership](guides/tmb-016.md)
17. [Shared effects versus separable blocks](guides/tmb-017.md)
18. [Prediction and uncertainty with sdreport](guides/tmb-018.md)
19. [Simulate, recover and criticize](guides/tmb-019.md)
20. [Parallel accumulators and OpenMP](guides/tmb-020.md)
21. [AFModel as a historical design case](guides/tmb-021.md)
22. [Pandas, NumPy and R conversion](guides/tmb-022.md)
23. [Python to a compiled TMB boundary](guides/tmb-023.md)
24. [A nonlinear forecast and uncertainty dossier](guides/tmb-024.md)

25. [From an empty template to a reviewed model](guides/tmb-025.md)
26. [MakeADFun maps, profiles and safe data changes](guides/tmb-026.md)
27. [CppAD, TMBad and derivative order](guides/tmb-027.md)
28. [Reporting objects and uncertainty controls](guides/tmb-028.md)
29. [Likelihood profiles versus slices](guides/tmb-029.md)
30. [Profile interval roots and boundary cases](guides/tmb-030.md)
31. [Simulation APIs and score consistency](guides/tmb-031.md)
32. [One-step-ahead predictive residuals](guides/tmb-032.md)
33. [Normalizing a latent process](guides/tmb-033.md)
34. [Alternative integration and sequential reduction](guides/tmb-034.md)
35. [The inner Newton solver and its controls](guides/tmb-035.md)
36. [Sparse symbolic analysis and factorization accuracy](guides/tmb-036.md)
37. [Compilation, ABI versions and native lifetime](guides/tmb-037.md)
38. [Debugging compiler and native failures](guides/tmb-038.md)
39. [Benchmarking explicit and automatic parallelism](guides/tmb-039.md)
40. [An API-complete workflow and qualification map](guides/tmb-040.md)

41. [Typed vectors, matrices, arrays and sparse inputs](guides/tmb-041.md)
42. [Stable distribution helpers and mixtures](guides/tmb-042.md)
43. [Multivariate normals and Gaussian Markov fields](guides/tmb-043.md)
44. [Separable arrays and scalar or vector scales](guides/tmb-044.md)
45. [Reporting and simulation inside the C++ model](guides/tmb-045.md)
46. [AD-safe branches, transforms and numerical domains](guides/tmb-046.md)
47. [Atomic functions and custom derivative contracts](guides/tmb-047.md)
48. [C++ model families and end-to-end acceptance](guides/tmb-048.md)

The [C++ model-authoring family map](CPP-API-FAMILIES.md) covers typed containers, macros, stable probability helpers, density composition and derivative extensions.

The [complete public API reference](API-REFERENCE.md) maps pinned exports, registered S3 methods and separately labeled documented helpers.

## Project and evidence

The [owned project](projects/tmb-local/README.md) contains original models, a fixed R API, a JSON evaluation boundary, a scoped rpy2 bridge and numerical tests. Read the [research and attribution record](RESEARCH.md) and [qualification ledger](QUALIFICATION.md) before making runtime claims.

The maintained classroom manifests are `track.json` and `lessons.json`. Stable chapter IDs are `tmb-001` through `tmb-048`; the ordinary runnable surface is the base-R companion, with native project capabilities labeled separately.
