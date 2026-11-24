import Foundation

enum Route: Hashable { case item(String) }
func parseRoute(_ text: String) -> Route? {
  guard let url = URLComponents(string: text), url.scheme == "journey", url.host == "item",
    url.query == nil, url.fragment == nil
  else { return nil }
  let parts = url.path.split(separator: "/")
  guard parts.count == 1 else { return nil }
  return .item(String(parts[0]))
}

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

    do {
      // Task 1: Predict and explain
      let parts = URLComponents(string: "journey://item/one")!
      precondition(parts.scheme == "journey" && parts.host == "item" && parts.path == "/one")
      precondition(parts.query == nil && parts.fragment == nil)
      precondition(parseRoute("journey://item/one?x=1") == nil)
      precondition(parseRoute("journey://item/one/two") == nil)
    }

    do {
      // Task 2: Guided modification
      enum AppRoute: Equatable {
        case overview
        case item(String)
      }
      func parseAppRoute(_ text: String) -> AppRoute? {
        guard let url = URLComponents(string: text), url.scheme == "journey", url.query == nil,
          url.fragment == nil
        else { return nil }
        let parts = url.path.split(separator: "/")
        switch (url.host, parts.count) {
        case ("overview"?, 0): return .overview
        case ("item"?, 1): return .item(String(parts[0]))
        default: return nil
        }
      }
      precondition(parseAppRoute("journey://overview") == .overview)
      precondition(parseAppRoute("journey://overview/extra") == nil)
      precondition(parseAppRoute("journey://item/one") == .item("one"))
    }

    do {
      // Task 4: Diagnose a defect
      let items = ["a": "Read", "b": "Practice"]
      var order = ["a", "b"]
      let selectedIndex = 0
      let selectedID = order[selectedIndex]
      order.reverse()
      precondition(items[order[selectedIndex]] == "Practice")
      precondition(items[selectedID] == "Read")
    }

    do {
      // Task 5: Boundary evidence
      precondition(parseRoute("journey://item/") == nil)
      var items = ["one": "Read"]
      let route = parseRoute("journey://item/one")
      items["one"] = nil
      var screen = "none"
      if case .item(let id)? = route { screen = items[id] ?? "Item unavailable" }
      precondition(screen == "Item unavailable")
    }
    print("swift-041: passed")
  }
}
