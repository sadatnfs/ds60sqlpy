using Test

struct Batch{T<:Real}
    values::Vector{T}
end

function typed_total(values::AbstractVector{T}) where {T<:Real}
    total = zero(T)
    for index in eachindex(values)
        total += values[index]
    end
    return total
end

accepts_reals(values::AbstractVector{<:Real}) = length(values)

# === EXAMPLE A ===
function worked_a()
    @test typed_total([1, 2, 3]) == 6
    @test typed_total([0.5, 1.5]) == 2.0
    @test typed_total([1//3, 2//3]) == 1//1
    @test (@inferred typed_total([1, 2])) == 3
    @test typed_total(Int[]) == 0
    println("Rational total: ", typed_total([1//3, 2//3]))
end

# === EXAMPLE B ===
function worked_b()
    integers = Batch([1, 2])
    floats = Batch([1.0, 2.0])
    @test integers isa Batch{Int}
    @test floats isa Batch{Float64}
    @test !(Vector{Float64} <: Vector{Real})
    @test Vector{Float64} <: AbstractVector{<:Real}
    @test accepts_reals(floats.values) == 2
    println("Batch types: ", typeof(integers), "; ", typeof(floats))
end

# === EXERCISES ===
function exercise_checks()
    @test typed_total(Float32[1, 2]) isa Float32
    @test typed_total(BigInt[1, 2]) == 3
    @test accepts_reals([1//2]) == 1
    @test_throws MethodError accepts_reals(["text"])
    @test !isconcretetype(AbstractVector{Float64})
    @test isconcretetype(Vector{Float64})
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-012: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
