import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let text = "é"
            precondition(text.count == 1)
            precondition(text.utf8.count == 2)
            let combined = "e\u{301}"
            precondition(combined.count == 1 && combined.utf8.count == 3)
        }

        do {
            let text = "A😀B"
            let firstEnd = text.index(after: text.startIndex)
            precondition(String(text[..<firstEnd]) == "A")
            precondition(String(text[firstEnd...]) == "😀B")
        }
        print("swift-004: passed")
    }
}
