## A decision record is more than a fitted model

This capstone studies a synthetic sensor calibration problem. Each row has a stable record ID, a numerical predictor and response, an assigned split, a prediction timestamp, a feature-availability timestamp and a label-availability timestamp. The authored table is deliberately small enough to audit by hand. It is not evidence that the same model works on real sensors.

The workflow validates identity, finite values, split membership and information timing before fitting anything. Features must have been available no later than the prediction timestamp. Labels must be available by the analysis cutoff. A future feature or missing final outcome cannot be quietly dropped to improve the reported score. Such changes alter the target population or information boundary and require a new declared protocol.

## Freeze selection before viewing the final split

The model is a line with an unpenalized intercept and a ridge penalty on its slope. For training matrix \(X\), response \(y\), coefficients \(\beta\) and nonnegative penalty \(\lambda\), minimize \(\lVert X\beta-y\rVert_2^2+\lambda\beta_2^2\). The reference uses augmented least squares rather than explicitly inverting a normal-equation matrix. Unit 21 derives the same small numerical mechanism; here it is embedded in an auditable data workflow.

Train candidate penalties 0,1,2 and 4 using only training rows. Select the smallest development mean squared error, using the declared candidate order to break an exact tie. Then compute the final error once for the selected candidate. Repeatedly changing features, candidates or preprocessing after reading final results would turn that final split into development data.

### Worked case A: carry one contract through the analysis

The first program parses the actual local CSV text, validates it and produces the selected coefficient and score record. The known result is \(\lambda=2\), \(\beta=(12/7,13/7)\), development MSE \(1/98\), and final MSE \(5/98\). These rational values provide an independent numerical oracle.

{{WORKED_A}}

A two-row final split has extremely limited statistical information. The result verifies the authored computation and demonstrates selection discipline. It does not provide a precise estimate of deployment risk, subgroup performance, causal impact or robustness to future distribution changes. A real study needs a sample-size and sampling-unit plan, uncertainty analysis and independent operational acceptance.

### Worked case B: a figure and its exact underlying table

The second complete program captures a Plotly comparison of final observations and predictions. It includes a textual description and exact table with IDs, targets, predictions and residuals. The JSON decision record contains the source fixture hash, selected penalty and split counts. The hash identifies bytes; it does not certify that the fixture is representative or truthful.

{{WORKED_B}}

## Challenge the workflow before trusting the report

The reference injects a duplicate ID, a late feature, a late final label and a nonfinite predictor. Each is rejected. This is stronger than merely checking that a normal CSV file can be parsed. Keep these failures visible in the learner's own extension. A transformation that silently removes difficult rows should be treated as a protocol change with explicit denominators.

The Plotly helper is classroom infrastructure, not a general Julia plotting package. It captures a bounded data artifact for the browser. Source execution, figure capture, browser rendering and saved receipts remain distinct acceptance layers. Outside the classroom, choose and prepare a plotting library explicitly rather than assuming this helper exists.

## The final memo and next steps

State the decision narrowly: the selected ridge candidate passes this synthetic numerical and data-contract demonstration; deployment is not approved by these observations alone. Record the frozen selection rule, independent final result, data identity and limitations. Propose the next evidence: a representative sampling plan, richer baselines, temporal validation, uncertainty and failure monitoring.

Use the [statistics book](../../../statistics-ml/README.md) and [LLM evaluation path](../../../llm-evaluation/README.md) for estimands, paired comparisons, leakage and selection uncertainty. Use the [applied-science projects](../../../applied-science/README.md) for deeper domain assumptions. Julia's language and numerical tools make an analysis executable; scientific design determines what its result can support.
