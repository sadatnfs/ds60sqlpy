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

# === EXAMPLE A ===
function worked_a()
    output = squared_pipeline(collect(1:5))
    @test output == [1, 4, 9, 16, 25]
    @test sum(output) == 55
    @test squared_pipeline(Int[]) == Int[]
    println("Joined pipeline result: ", output)
end

# === EXAMPLE B ===
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

# === EXERCISES ===
function exercise_checks()
    @test squared_pipeline([-2, 0, 3]) == [4, 0, 9]
    @test squared_pipeline([2, 2]) == [4, 4]
    @test_throws CompositeException squared_pipeline([1]; fail_after = 0)
    job = @async 6 * 7
    @test fetch(job) == 42
    @test istaskdone(job)
    @test squared_pipeline([4]) == [16]
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-029: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
