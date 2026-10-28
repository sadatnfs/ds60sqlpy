using Test

function worked_b()
    counts = Dict{String,Int}()
    for label in ["b", "a", "b"]
        counts[label] = get(counts, label, 0) + 1
    end
    @test counts == Dict("a" => 1, "b" => 2)
    @test sort(collect(keys(counts))) == ["a", "b"]
    @test Set(["b", "a", "b"]) == Set(["a", "b"])
    println("Ordered counts: ", [(key, counts[key]) for key in sort(collect(keys(counts)))])
end

worked_b()
