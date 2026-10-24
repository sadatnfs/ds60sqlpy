import Foundation

enum Route: Hashable { case item(String) }
func parseRoute(_ text: String) -> Route? { guard let url = URLComponents(string: text), url.scheme == "journey", url.host == "item", url.query == nil, url.fragment == nil else { return nil }; let parts = url.path.split(separator: "/"); guard parts.count == 1 else { return nil }; return .item(String(parts[0])) }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let route = parseRoute("journey://item/one")
            precondition(route == .item("one"))
        }

        do {
            precondition(parseRoute("https://example.invalid/one") == nil)
            precondition(parseRoute("journey://item/") == nil)
            precondition(parseRoute("journey://delete/one") == nil)
        }
        print("swift-041: passed")
    }
}
