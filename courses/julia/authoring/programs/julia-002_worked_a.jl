using Test

function worked_a()
    top = typemax(Int8)
    @test top + Int8(1) == typemin(Int8)
    @test_throws OverflowError Base.Checked.checked_add(top, Int8(1))
    @test BigInt(top) + 1 == 128
    println("Wrapped: ", top + Int8(1), "; exact: ", BigInt(top) + 1)
end

worked_a()
