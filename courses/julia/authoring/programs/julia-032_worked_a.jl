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
