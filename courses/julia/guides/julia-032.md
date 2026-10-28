# julia-032: Scientific capstone: an auditable offline modeling report

## Starting point and outcome

Advanced; approximately 150 minutes. Direct prerequisites: `julia-016`, `julia-017`, `julia-018`, `julia-021`, `julia-024`, `julia-028`.

Execute a complete synthetic modeling workflow from typed CSV to a source-identified decision record, exact numerical checks and an accessible Plotly report.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A decision record is more than a fitted model

This capstone studies a synthetic sensor calibration problem. Each row has a stable record ID, a numerical predictor and response, an assigned split, a prediction timestamp, a feature-availability timestamp and a label-availability timestamp. The authored table is deliberately small enough to audit by hand. It is not evidence that the same model works on real sensors.

The workflow validates identity, finite values, split membership and information timing before fitting anything. Features must have been available no later than the prediction timestamp. Labels must be available by the analysis cutoff. A future feature or missing final outcome cannot be quietly dropped to improve the reported score. Such changes alter the target population or information boundary and require a new declared protocol.

## Freeze selection before viewing the final split

The model is a line with an unpenalized intercept and a ridge penalty on its slope. For training matrix \(X\), response \(y\), coefficients \(\beta\) and nonnegative penalty \(\lambda\), minimize \(\lVert X\beta-y\rVert_2^2+\lambda\beta_2^2\). The reference uses augmented least squares rather than explicitly inverting a normal-equation matrix. Unit 21 derives the same small numerical mechanism; here it is embedded in an auditable data workflow.

Train candidate penalties 0,1,2 and 4 using only training rows. Select the smallest development mean squared error, using the declared candidate order to break an exact tie. Then compute the final error once for the selected candidate. Repeatedly changing features, candidates or preprocessing after reading final results would turn that final split into development data.

### Worked case A: carry one contract through the analysis

The first program parses the actual local CSV text, validates it and produces the selected coefficient and score record. The known result is \(\lambda=2\), \(\beta=(12/7,13/7)\), development MSE \(1/98\), and final MSE \(5/98\). These rational values provide an independent numerical oracle.

```julia
using Test
using CSV
using DataFrames
using Dates
using LinearAlgebra
using Statistics
using JSON3
using SHA
using .DS60Plots
BLAS.set_num_threads(1)

const SENSOR_CSV = """id,x,y,split,prediction_at,feature_available_at,label_available_at
s01,0,1,train,2024-01-01,2023-12-31,2024-01-02
s02,1,3,train,2024-01-02,2024-01-01,2024-01-03
s03,2,5,train,2024-01-03,2024-01-02,2024-01-04
s04,3,9,train,2024-01-04,2024-01-03,2024-01-05
s05,4,9,development,2024-01-05,2024-01-04,2024-01-06
s06,5,11,development,2024-01-06,2024-01-05,2024-01-07
s07,6,13,final,2024-01-07,2024-01-06,2024-01-08
s08,7,15,final,2024-01-08,2024-01-07,2024-01-09
"""

function load_sensor(text = SENSOR_CSV)
    types = Dict(
        :id => String,
        :x => Float64,
        :y => Float64,
        :split => String,
        :prediction_at => Date,
        :feature_available_at => Date,
        :label_available_at => Date,
    )
    return CSV.read(IOBuffer(text), DataFrame; types = types, strict = true)
end

function validate_sensor(table; cutoff = Date(2024, 1, 10))
    nrow(table) == 8 || throw(ArgumentError("The declared fixture requires eight rows"))
    any(any(ismissing, column) for column in eachcol(table)) &&
        throw(ArgumentError("All declared fields are required"))
    length(unique(table.id)) == nrow(table) || throw(ArgumentError("Duplicate record ID"))
    all(value -> !isempty(value), table.id) || throw(ArgumentError("Empty record ID"))
    all(isfinite, table.x) && all(isfinite, table.y) ||
        throw(ArgumentError("Nonfinite scientific value"))
    Set(table.split) == Set(["train", "development", "final"]) ||
        throw(ArgumentError("Unknown or absent split"))
    all(table.feature_available_at .<= table.prediction_at) ||
        throw(ArgumentError("Feature information arrived too late"))
    all(table.label_available_at .<= cutoff) ||
        throw(ArgumentError("Label unavailable by analysis cutoff"))
    counts =
        Dict(split => count(==(split), table.split) for split in ("train", "development", "final"))
    counts == Dict("train" => 4, "development" => 2, "final" => 2) ||
        throw(ArgumentError("Split denominators changed"))
    return counts
end

function ridge_fit(x, y, penalty)
    design = hcat(ones(length(x)), x)
    augmented = vcat(design, reshape([0.0, sqrt(penalty)], 1, 2))
    return augmented \ vcat(y, 0.0)
end
predict_line(beta, x) = beta[1] .+ beta[2] .* x
score(predicted, actual) = mean(abs2, predicted .- actual)

function analyze(text = SENSOR_CSV)
    table = load_sensor(text)
    counts = validate_sensor(table)
    train = subset(table, :split => ByRow(==("train")))
    development = subset(table, :split => ByRow(==("development")))
    final = subset(table, :split => ByRow(==("final")))
    penalties = [0.0, 1.0, 2.0, 4.0]
    fits = [ridge_fit(train.x, train.y, penalty) for penalty in penalties]
    errors = [score(predict_line(beta, development.x), development.y) for beta in fits]
    selected = argmin(errors)
    beta = fits[selected]
    predictions = predict_line(beta, final.x)
    memo = Dict(
        "fixture_sha256" => bytes2hex(sha256(text)),
        "split_counts" => counts,
        "penalty" => penalties[selected],
        "coefficients" => beta,
        "development_mse" => errors[selected],
        "final_mse" => score(predictions, final.y),
        "decision" => "Synthetic workflow verified; deployment evidence remains insufficient",
    )
    return (memo = memo, final = final, predictions = predictions)
end

function worked_a()
    result = analyze()
    @test result.memo["penalty"] == 2
    @test result.memo["coefficients"] ≈ [12/7, 13/7]
    @test result.memo["development_mse"] ≈ 1/98
    @test result.memo["final_mse"] ≈ 5/98
    @test result.memo["split_counts"] == Dict("train" => 4, "development" => 2, "final" => 2)
    println("Decision record: ", JSON3.write(result.memo))
end

worked_a()
```

A two-row final split has extremely limited statistical information. The result verifies the authored computation and demonstrates selection discipline. It does not provide a precise estimate of deployment risk, subgroup performance, causal impact or robustness to future distribution changes. A real study needs a sample-size and sampling-unit plan, uncertainty analysis and independent operational acceptance.

### Worked case B: a figure and its exact underlying table

The second complete program captures a Plotly comparison of final observations and predictions. It includes a textual description and exact table with IDs, targets, predictions and residuals. The JSON decision record contains the source fixture hash, selected penalty and split counts. The hash identifies bytes; it does not certify that the fixture is representative or truthful.

```julia
using Test
using CSV
using DataFrames
using Dates
using LinearAlgebra
using Statistics
using JSON3
using SHA
using .DS60Plots
BLAS.set_num_threads(1)

const SENSOR_CSV = """id,x,y,split,prediction_at,feature_available_at,label_available_at
s01,0,1,train,2024-01-01,2023-12-31,2024-01-02
s02,1,3,train,2024-01-02,2024-01-01,2024-01-03
s03,2,5,train,2024-01-03,2024-01-02,2024-01-04
s04,3,9,train,2024-01-04,2024-01-03,2024-01-05
s05,4,9,development,2024-01-05,2024-01-04,2024-01-06
s06,5,11,development,2024-01-06,2024-01-05,2024-01-07
s07,6,13,final,2024-01-07,2024-01-06,2024-01-08
s08,7,15,final,2024-01-08,2024-01-07,2024-01-09
"""

function load_sensor(text = SENSOR_CSV)
    types = Dict(
        :id => String,
        :x => Float64,
        :y => Float64,
        :split => String,
        :prediction_at => Date,
        :feature_available_at => Date,
        :label_available_at => Date,
    )
    return CSV.read(IOBuffer(text), DataFrame; types = types, strict = true)
end

function validate_sensor(table; cutoff = Date(2024, 1, 10))
    nrow(table) == 8 || throw(ArgumentError("The declared fixture requires eight rows"))
    any(any(ismissing, column) for column in eachcol(table)) &&
        throw(ArgumentError("All declared fields are required"))
    length(unique(table.id)) == nrow(table) || throw(ArgumentError("Duplicate record ID"))
    all(value -> !isempty(value), table.id) || throw(ArgumentError("Empty record ID"))
    all(isfinite, table.x) && all(isfinite, table.y) ||
        throw(ArgumentError("Nonfinite scientific value"))
    Set(table.split) == Set(["train", "development", "final"]) ||
        throw(ArgumentError("Unknown or absent split"))
    all(table.feature_available_at .<= table.prediction_at) ||
        throw(ArgumentError("Feature information arrived too late"))
    all(table.label_available_at .<= cutoff) ||
        throw(ArgumentError("Label unavailable by analysis cutoff"))
    counts =
        Dict(split => count(==(split), table.split) for split in ("train", "development", "final"))
    counts == Dict("train" => 4, "development" => 2, "final" => 2) ||
        throw(ArgumentError("Split denominators changed"))
    return counts
end

function ridge_fit(x, y, penalty)
    design = hcat(ones(length(x)), x)
    augmented = vcat(design, reshape([0.0, sqrt(penalty)], 1, 2))
    return augmented \ vcat(y, 0.0)
end
predict_line(beta, x) = beta[1] .+ beta[2] .* x
score(predicted, actual) = mean(abs2, predicted .- actual)

function analyze(text = SENSOR_CSV)
    table = load_sensor(text)
    counts = validate_sensor(table)
    train = subset(table, :split => ByRow(==("train")))
    development = subset(table, :split => ByRow(==("development")))
    final = subset(table, :split => ByRow(==("final")))
    penalties = [0.0, 1.0, 2.0, 4.0]
    fits = [ridge_fit(train.x, train.y, penalty) for penalty in penalties]
    errors = [score(predict_line(beta, development.x), development.y) for beta in fits]
    selected = argmin(errors)
    beta = fits[selected]
    predictions = predict_line(beta, final.x)
    memo = Dict(
        "fixture_sha256" => bytes2hex(sha256(text)),
        "split_counts" => counts,
        "penalty" => penalties[selected],
        "coefficients" => beta,
        "development_mse" => errors[selected],
        "final_mse" => score(predictions, final.y),
        "decision" => "Synthetic workflow verified; deployment evidence remains insufficient",
    )
    return (memo = memo, final = final, predictions = predictions)
end

function worked_b()
    result = analyze()
    final = result.final
    predictions = result.predictions
    rows = [
        [String(final.id[i]), final.y[i], predictions[i], predictions[i] - final.y[i]] for
        i = 1:nrow(final)
    ]
    data = [
        Dict(
            "type" => "scatter",
            "mode" => "markers",
            "name" => "Final observations",
            "x" => final.x,
            "y" => final.y,
        ),
        Dict(
            "type" => "scatter",
            "mode" => "lines+markers",
            "name" => "Frozen selected model",
            "x" => final.x,
            "y" => predictions,
        ),
    ]
    layout = Dict(
        "title" => "Synthetic final split after frozen selection",
        "xaxis" => Dict("title" => "Predictor"),
        "yaxis" => Dict("title" => "Response"),
        "meta" => Dict(
            "description" => "Two authored final records compare a development-selected ridge line with their known outcomes. This is a numerical workflow demonstration, not deployment evidence.",
            "table" => Dict(
                "columns" => ["ID", "Observed", "Predicted", "Residual"],
                "rows" => rows,
            ),
        ),
    )
    show_plotly(
        data;
        layout = layout,
        description = "Synthetic held-out observations and frozen predictions",
    )
    @test predictions ≈ [90/7, 103/7]
    @test length(result.memo["fixture_sha256"]) == 64
    @test JSON3.read(JSON3.write(result.memo))["penalty"] == 2
    println("Exact final table: ", rows)
end

worked_b()
```

## Challenge the workflow before trusting the report

The reference injects a duplicate ID, a late feature, a late final label and a nonfinite predictor. Each is rejected. This is stronger than merely checking that a normal CSV file can be parsed. Keep these failures visible in the learner's own extension. A transformation that silently removes difficult rows should be treated as a protocol change with explicit denominators.

The Plotly helper is classroom infrastructure, not a general Julia plotting package. It captures a bounded data artifact for the browser. Source execution, figure capture, browser rendering and saved receipts remain distinct acceptance layers. Outside the classroom, choose and prepare a plotting library explicitly rather than assuming this helper exists.

## The final memo and next steps

State the decision narrowly: the selected ridge candidate passes this synthetic numerical and data-contract demonstration; deployment is not approved by these observations alone. Record the frozen selection rule, independent final result, data identity and limitations. Propose the next evidence: a representative sampling plan, richer baselines, temporal validation, uncertainty and failure monitoring.

Use the [statistics book](../../statistics-ml/README.md) and [LLM evaluation path](../../llm-evaluation/README.md) for estimands, paired comparisons, leakage and selection uncertainty. Use the [applied-science projects](../../applied-science/README.md) for deeper domain assumptions. Julia's language and numerical tools make an analysis executable; scientific design determines what its result can support.


## Six investigations

### 1. Audit the grain

Explain what one row and one ID represent.

**Expected:** One synthetic prediction record with declared availability evidence.

**Hint:** Distinct IDs prevent accidental duplication.

### 2. Reproduce the selection

Compare development errors for the four fixed penalties.

**Expected:** Penalty 2 is selected.

**Hint:** Do not inspect final outcomes to choose candidates.

### 3. Verify final arithmetic

Compute residuals for predictions 90/7 and 103/7 against 13 and 15.

**Expected:** Residuals are -1/7 and -2/7; MSE is 5/98.

**Hint:** Square and average the two errors.

### 4. Inject information leakage

Move a feature availability date after its prediction date.

**Expected:** The data validator rejects the fixture.

**Hint:** Event meaning and availability differ.

### 5. Inspect accessible evidence

Compare each Plotly table row with its plotted observation and prediction.

**Expected:** The values and IDs must match exactly.

**Hint:** The chart is a view of the same final data.

### 6. Write the decision memo

State what passes and what evidence is still missing.

**Expected:** Synthetic computation passes; deployment is not justified.

**Hint:** Mention small final sample and selection history.

## Primary references

- [CSV 0.10 reading contract](https://github.com/JuliaData/CSV.jl/blob/v0.10.17/docs/src/reading.md)
- [DataFrames split transformations](https://dataframes.juliadata.org/stable/man/split_apply_combine/)
- [LinearAlgebra](https://docs.julialang.org/en/v1/stdlib/LinearAlgebra/)
- [JSON3 interface](https://quinnj.github.io/JSON3.jl/stable/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.
