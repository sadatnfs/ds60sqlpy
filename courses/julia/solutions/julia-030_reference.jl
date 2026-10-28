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

# === EXAMPLE B ===
function worked_b()
    @test locked_counter(4, 100) == 400
    @test locked_counter(0, 100) == 0
    @test locked_counter(2, 0) == 0
    @test_throws ArgumentError locked_counter(2, -1)
    println("Joined protected increments: ", locked_counter(4, 100))
end

# === EXERCISES ===
function exercise_checks()
    @test chunk_squares([-2, 3]) == 13
    @test chunk_squares([0, 0]) == 0
    @test locked_counter(1, 7) == 7
    @test_throws ArgumentError locked_counter(-1, 2)
    values = [1, 2, 3]
    before = copy(values)
    @test chunk_squares(values) == 14
    @test values == before
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-030: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
