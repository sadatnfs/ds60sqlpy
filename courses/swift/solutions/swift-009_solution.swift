import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let original = [1, 2]
            var changed = original
            changed.append(3)
            precondition(original == [1, 2])
            precondition(changed == [1, 2, 3])
        }

        do {
            var values: [Int] = []
            values.reserveCapacity(20)
            precondition(values.count == 0)
            values.append(7)
            precondition(values.count == 1 && values[0] == 7)
        }
        print("swift-009: passed")
    }
}
