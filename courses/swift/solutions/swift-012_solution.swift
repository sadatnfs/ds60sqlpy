import Foundation

struct Inventory { private(set) var stock: Int; mutating func reserve(_ amount: Int) -> Bool { guard amount >= 0, amount <= stock else { return false }; stock -= amount; return true } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            var first = Inventory(stock: 5)
            var second = first
            precondition(second.reserve(2))
            precondition(first.stock == 5 && second.stock == 3)
            precondition(first.reserve(0))
        }

        do {
            var inventory = Inventory(stock: 3)
            precondition(!inventory.reserve(4))
            precondition(!inventory.reserve(-1))
            precondition(inventory.stock == 3)
        }
        print("swift-012: passed")
    }
}
