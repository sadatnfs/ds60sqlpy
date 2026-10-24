import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let values = [2, 4, 6]
            var total = 0
            for value in values { total += value }
            precondition(total == 12)
            precondition([Int]().reduce(0, +) == 0)
        }

        do {
            let values = [3, 8, 8]
            var found: Int? = nil
            for (offset, value) in values.enumerated() { if value == 8 { found = offset; break } }
            precondition(found == 1)
            precondition(values.firstIndex(of: 9) == nil)
        }
        print("swift-007: passed")
    }
}
