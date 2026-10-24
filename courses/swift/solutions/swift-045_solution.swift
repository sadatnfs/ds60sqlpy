import Foundation

struct TextBridgeState {
  var text: String
  var assignments: Int
  mutating func update(_ incoming: String) {
    guard text != incoming else { return }
    text = incoming
    assignments += 1
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var bridge = TextBridgeState(text: "old", assignments: 0)
      bridge.update("new")
      bridge.update("new")
      precondition(bridge.text == "new" && bridge.assignments == 1)
    }

    do {
      var bridge = TextBridgeState(text: "start", assignments: 0)
      bridge.update("edited")
      precondition(bridge.text == "edited")
      precondition(bridge.assignments == 1)
    }
    print("swift-045: passed")
  }
}
