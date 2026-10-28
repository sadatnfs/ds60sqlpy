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

function worked_a()
    @test typed_total([1, 2, 3]) == 6
    @test typed_total([0.5, 1.5]) == 2.0
    @test typed_total([1//3, 2//3]) == 1//1
    @test (@inferred typed_total([1, 2])) == 3
    @test typed_total(Int[]) == 0
    println("Rational total: ", typed_total([1//3, 2//3]))
end

worked_a()
