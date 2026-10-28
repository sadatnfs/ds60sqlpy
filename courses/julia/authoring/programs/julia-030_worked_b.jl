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

function worked_b()
    @test locked_counter(4, 100) == 400
    @test locked_counter(0, 100) == 0
    @test locked_counter(2, 0) == 0
    @test_throws ArgumentError locked_counter(2, -1)
    println("Joined protected increments: ", locked_counter(4, 100))
end

worked_b()
