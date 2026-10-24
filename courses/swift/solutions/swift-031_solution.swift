import Foundation

actor CounterActor { private(set) var value = 0; func increment() { value += 1 } }
actor InventoryActor { private(set) var stock: Int; init(stock: Int) { self.stock = stock }; func reserve(_ amount: Int) -> Bool { guard amount >= 0 && amount <= stock else { return false }; stock -= amount; return true } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let counter = CounterActor()
            await withTaskGroup(of: Void.self) { group in for _ in 0..<20 { group.addTask { await counter.increment() } } }
            let value = await counter.value
            precondition(value == 20)
        }

        do {
            let inventory = InventoryActor(stock: 3)
            let first = await inventory.reserve(2)
            let second = await inventory.reserve(2)
            let remaining = await inventory.stock
            precondition(first && !second && remaining == 1)
        }
        print("swift-031: passed")
    }
}
