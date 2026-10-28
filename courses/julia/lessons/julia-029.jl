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

worked_a()

# Task 1: Describe what happens when a producer fills a capacity-two buffer.
# Task 2: Predict the output for[-2,0,3].
# Task 3: Set fail_after=0 on a nonempty list.
# Task 4: Put 7 into a channel, close it, then collect it.
# Task 5: Explain what can go wrong if an arbitrary consumer callback throws.
# Task 6: Specify identifiers and completion evidence for concurrent files.

# Write your independent changes below.
