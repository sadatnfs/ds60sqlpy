import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let values = [1, 2, 3]
            let doubled = values.map { value in value * 2 }
            precondition(doubled == [2, 4, 6])
            precondition(values == [1, 2, 3])
        }

        do {
            var factor = 2
            let scale = { [factor] (value: Int) in value * factor }
            factor = 5
            precondition(scale(3) == 6 && factor == 5)
        }
        print("swift-015: passed")
    }
}
