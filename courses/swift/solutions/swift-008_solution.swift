import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            func area(width: Int, height: Int) -> Int { width * height }
            precondition(area(width: 3, height: 4) == 12)
            precondition(area(width: 0, height: 4) == 0)
        }

        do {
            func increment(_ value: inout Int) { value += 1 }
            var count = 4
            increment(&count)
            precondition(count == 5)
        }
        print("swift-008: passed")
    }
}
