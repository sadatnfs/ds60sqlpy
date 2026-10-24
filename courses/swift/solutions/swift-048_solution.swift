import Foundation

struct CapstoneItem: Equatable, Sendable { let id: String; var complete: Bool }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let items = [CapstoneItem(id: "a", complete: true), CapstoneItem(id: "b", complete: false)]
            precondition(items.filter(\.complete).count == 1)
            precondition(Set(items.map(\.id)).count == items.count)
        }

        do {
            let original = CapstoneItem(id: "a", complete: false)
            var changed = original
            changed.complete = true
            precondition(changed.id == original.id && !original.complete && changed.complete)
        }
        print("swift-048: passed")
    }
}
