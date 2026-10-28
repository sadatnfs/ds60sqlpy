using Test

affine(x; scale = 1, shift = 0) = scale * x + shift
make_scaler(scale) = x -> scale * x

function rebind(values)
    values = [99]
    return values
end

function change_first!(values)
    isempty(values) && throw(ArgumentError("A first element is required"))
    values[1] = 99
    return values
end

function worked_b()
    values = [1, 2]
    replacement = rebind(values)
    @test values == [1, 2]
    @test replacement == [99]
    returned = change_first!(values)
    @test values == [99, 2]
    @test returned === values
    println("Caller-visible mutation: ", values)
end

worked_b()
