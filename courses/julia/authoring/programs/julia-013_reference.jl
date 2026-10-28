using Test

# === EXAMPLE A ===
function worked_a()
    matrix = [1 3 5; 2 4 6]
    rows = [10, 20]
    columns = reshape([100, 200, 300], 1, 3)
    result = matrix .+ rows .+ columns
    @test result == [111 213 315; 122 224 326]
    @test_throws DimensionMismatch matrix .+ [1, 2, 3, 4]
    println("Broadcast result: ", result)
end

# === EXAMPLE B ===
function worked_b()
    values = [1.0, 2.0, 3.0]
    values .= 2 .* values .+ 1
    @test values == [3, 5, 7]
    sequential = [1, 2, 3, 4]
    for index = 2:length(sequential)
        sequential[index] = sequential[index-1]
    end
    snapshot = [1, 2, 3, 4]
    source = copy(snapshot)
    for index = 2:length(snapshot)
        snapshot[index] = source[index-1]
    end
    @test sequential == [1, 1, 1, 1]
    @test snapshot == [1, 1, 2, 3]
    println("Sequential versus snapshot: ", sequential, "; ", snapshot)
end

# === EXERCISES ===
function exercise_checks()
    @test sin.([0.0, pi/2]) ≈ [0, 1]
    @test [1, 2] .+ 3 == [4, 5]
    @test size(reshape([1, 2, 3], 1, 3)) == (1, 3)
    @test [1, 2] .* [3, 4] == [3, 8]
    destination = zeros(2)
    destination .= [1, 2] ./ 2
    @test destination == [0.5, 1.0]
    @test_throws InexactError Int[0] .= [0.5]
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-013: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
