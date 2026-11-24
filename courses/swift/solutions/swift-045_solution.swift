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

    do {
      // Task 1: Predict and explain
      var bridge = TextBridgeState(text: "", assignments: 0)
      let renders = ["draft", "draft", "final"]
      for value in renders { bridge.update(value) }
      precondition(bridge.text == "final" && bridge.assignments == 2)
    }

    do {
      // Task 2: Guided modification
      var bridge = TextBridgeState(text: "same", assignments: 0)
      bridge.update("same")
      precondition(bridge.assignments == 0)
      bridge.update("other")
      precondition(bridge.assignments == 1)
    }

    do {
      // Task 4: Diagnose a defect
      var writes = 0
      var value = "a"
      func callback(_ incoming: String, depth: Int) {
        guard depth < 5 else { return }
        guard incoming != value else { return }
        value = incoming
        writes += 1
        callback(incoming, depth: depth + 1)
      }
      callback("b", depth: 0)
      precondition(writes == 1 && value == "b")
    }

    do {
      // Task 5: Boundary evidence
      var bridge = TextBridgeState(text: "x", assignments: 0)
      bridge.update("")
      precondition(bridge.text.isEmpty && bridge.assignments == 1)
      let large = String(repeating: "a", count: 100_000)
      bridge.update(large)
      bridge.update(large)
      precondition(bridge.text.count == 100_000 && bridge.assignments == 2)
    }
    print("swift-045: passed")
  }
}
