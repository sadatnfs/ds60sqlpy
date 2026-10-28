using Test

function chunk_squares(values::Vector{Int})
    isempty(values) && return 0
    middle = cld(length(values), 2)
    ranges = [1:middle, (middle+1):length(values)]
    jobs = [
        Threads.@spawn(sum(value -> value * value, view(values, range); init = 0)) for
        range in ranges
    ]
    return sum(fetch(job) for job in jobs)
end

function locked_counter(workers::Int, increments::Int)
    workers >= 0 && increments >= 0 || throw(ArgumentError("Nonnegative work counts required"))
    guard = ReentrantLock()
    counter = Ref(0)
    @sync for _ = 1:workers
        Threads.@spawn begin
            for _ = 1:increments
                lock(guard) do
                    counter[] += 1
                end
            end
        end
    end
    return counter[]
end

# === EXAMPLE A ===
function worked_a()
    values = collect(1:100)
    @test Threads.nthreads() == 2
    @test chunk_squares(values) == 338350
    @test chunk_squares(Int[]) == 0
    @test chunk_squares([3]) == 9
    @test all(chunk_squares(values) == 338350 for _ = 1:5)
    println("Two-thread chunk reduction: ", chunk_squares(values))
end

worked_a()

# Task 1: Compute the sum of squares through 100 from the closed-form formula.
# Task 2: Explain how the single-element input handles its second range.
# Task 3: Trace two unprotected increments that read the same value.
# Task 4: Explain why threadid-indexed buffers can be unsafe.
# Task 5: Explain why changing grouping can change floating results.
# Task 6: State the boundaries needed to claim a parallel speedup.

# Write your independent changes below.
