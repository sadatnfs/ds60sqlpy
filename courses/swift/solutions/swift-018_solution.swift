import Foundation

func larger<T: Comparable>(_ left: T, _ right: T) -> T { left >= right ? left : right }
struct Pair<T> { let first: T; let second: T; func swapped() -> Pair<T> { Pair(first: second, second: first) } }

@main
struct LessonMain {
    static func main() async throws {
        do {
            precondition(larger(3, 8) == 8)
            precondition(larger("apple", "pear") == "pear")
        }

        do {
            let pair = Pair(first: "left", second: "right")
            let swapped = pair.swapped()
            precondition(swapped.first == "right" && swapped.second == "left")
        }
        print("swift-018: passed")
    }
}
