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

    do {
      // Task 2: Guided modification
      func volume(width: Int, height: Int, depth: Int) -> Int { width * height * depth }
      precondition(volume(width: 2, height: 3, depth: 4) == 24)
      precondition(volume(width: 2, height: 3, depth: 0) == 0)
    }

    do {
      // Task 3: Independent construction
      func normalized(_ quantity: Int, limit: Int) -> Int {
        min(max(quantity, 0), limit)
      }
      let requested = 15
      precondition(normalized(requested, limit: 10) == 10)
      precondition(normalized(-4, limit: 10) == 0 && requested == 15)
    }

    do {
      // Task 5: Boundary evidence
      func checkedArea(width: Int, height: Int) -> Int? {
        guard width >= 0, height >= 0 else { return nil }
        return width * height
      }
      precondition(checkedArea(width: 0, height: 4) == 0)
      precondition(checkedArea(width: -3, height: 4) == nil)
      precondition(checkedArea(width: -3, height: -4) == nil)
    }
    print("swift-008: passed")
  }
}
