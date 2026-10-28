using Test

function squared_pipeline(values::Vector{Int}; fail_after = nothing)
    channel = Channel{Int}(2)
    output = Int[]
    @sync begin
        @async begin
            try
                for (index, value) in enumerate(values)
                    fail_after !== nothing &&
                        index > fail_after &&
                        error("Authored producer failure")
                    put!(channel, value)
                end
            finally
                close(channel)
            end
        end
        @async begin
            for value in channel
                push!(output, value * value)
            end
        end
    end
    return output
end

function worked_a()
    output = squared_pipeline(collect(1:5))
    @test output == [1, 4, 9, 16, 25]
    @test sum(output) == 55
    @test squared_pipeline(Int[]) == Int[]
    println("Joined pipeline result: ", output)
end

worked_a()
