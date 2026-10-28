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

worked_b()
