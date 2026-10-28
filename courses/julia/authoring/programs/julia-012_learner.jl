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

worked_a()

# Task 1: Sum 1//3 and 2//3.
# Task 2: Sum Int[].
# Task 3: Test whether Vector{Float64} is a subtype of Vector{Real}.
# Task 4: Use AbstractVector{<:Real} in a method signature.
# Task 5: Pass a vector of strings to the real-vector method.
# Task 6: Explain why an output buffer should not always be Float64.

# Write your independent changes below.
