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

    do {
      // Task 1: Predict and explain
      let original = [1, 2]
      var changed = original
      changed.append(3)
      precondition(original == [1, 2] && original.count == 2)
      precondition(changed == [1, 2, 3] && changed.count == 3)
    }

    do {
      // Task 2: Guided modification
      let original = [1, 2, 3]
      var copy = original
      copy[0] = 10
      precondition(copy == [10, 2, 3])
      precondition(original == [1, 2, 3])
    }

    do {
      // Task 3: Independent construction
      let source = [-1, 2, -3, 4]
      let positives = source.filter { $0 > 0 }
      precondition(positives == [2, 4])
      precondition(source == [-1, 2, -3, 4])
    }

    do {
      // Task 4: Diagnose a defect
      var values: [Int] = []
      values.reserveCapacity(20)
      precondition(values.capacity >= 20 && values.isEmpty)
      precondition(!values.indices.contains(0))
      values.append(7)
      precondition(values.indices.contains(0) && values[0] == 7)
    }

    do {
      // Task 5: Boundary evidence
      let values = [10, 20, 30, 40]
      let empty = values[2..<2]
      precondition(empty.isEmpty && empty.startIndex == 2)
      let tail = values[1...]
      precondition(tail.startIndex == 1 && tail.first == 20)
      precondition(tail[tail.startIndex] == 20 && tail[1] == 20)
    }
    print("swift-009: passed")
  }
}
