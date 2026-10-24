import Foundation

struct LoadState {
  var generation: Int
  var title: String?
  mutating func accept(_ value: String, generation candidate: Int) {
    guard candidate == generation else { return }
    title = value
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var state = LoadState(generation: 2, title: nil)
      state.accept("new", generation: 2)
      precondition(state.title == "new")
    }

    do {
      var state = LoadState(generation: 2, title: "new")
      state.accept("old", generation: 1)
      precondition(state.title == "new")
    }
    print("swift-043: passed")
  }
}
