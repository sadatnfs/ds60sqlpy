import Foundation

final class Counter { private(set) var value = 0; func increment() { value += 1 } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let first = Counter()
            let second = first
            second.increment()
            precondition(first.value == 1)
            precondition(first === second)
        }

        do {
            let first = Counter()
            let second = Counter()
            precondition(first.value == second.value)
            precondition(first !== second)
        }
        print("swift-013: passed")
    }
}
