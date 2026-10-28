"""Bounded classroom Plotly output. The server validates every artifact again."""
module DS60Plots
using JSON3
export show_plotly
const OUTPUT_DIRECTORY = pwd()
function show_plotly(data; layout = Dict{String,Any}(), description = "Julia figure")
    path = joinpath(OUTPUT_DIRECTORY, "ds60-figures.json")
    artifacts =
        isfile(path) ? JSON3.read(read(path, String), Vector{Dict{String,Any}}) : Dict{String,Any}[]
    length(artifacts) < 2 || throw(ArgumentError("At most two classroom figures are retained"))
    figure = Dict("data" => data, "layout" => layout)
    artifact =
        Dict{String,Any}("kind" => "plotly", "figure" => figure, "description" => description)
    ncodeunits(JSON3.write(artifact)) <= 180000 ||
        throw(ArgumentError("Figure exceeds the classroom byte limit"))
    push!(artifacts, artifact)
    encoded = JSON3.write(artifacts)
    ncodeunits(encoded) <= 384000 ||
        throw(ArgumentError("Combined figures exceed the classroom byte limit"))
    temporary, stream = mktemp(OUTPUT_DIRECTORY)
    try
        write(stream, encoded)
        close(stream)
        Base.Filesystem.rename(temporary, path)
    finally
        isopen(stream) && close(stream)
        isfile(temporary) && rm(temporary)
    end
    return nothing
end
end
