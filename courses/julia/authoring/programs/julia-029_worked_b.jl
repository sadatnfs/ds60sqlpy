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

function worked_b()
    @test_throws CompositeException squared_pipeline([1, 2, 3]; fail_after = 1)
    channel = Channel{Int}(1)
    put!(channel, 7)
    close(channel)
    @test collect(channel) == [7]
    @test !isopen(channel)
    @test_throws InvalidStateException put!(channel, 8)
    println("Producer failure propagated and closed channel drained")
end

worked_b()
