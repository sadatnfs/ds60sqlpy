import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [2, 4, 6]
      var total = 0
      for value in values { total += value }
      precondition(total == 12)
      precondition([Int]().reduce(0, +) == 0)
    }

    do {
      let values = [3, 8, 8]
      var found: Int? = nil
      for (offset, value) in values.enumerated() {
        if value == 8 {
          found = offset
          break
        }
      }
      precondition(found == 1)
      precondition(values.firstIndex(of: 9) == nil)
    }

    do {
      // Task 1: Predict and explain
      let values = [2, 4, 6]
      var total = 0
      var trace: [Int] = []
      for value in values {
        total += value
        trace.append(total)
      }
      precondition(trace == [2, 6, 12] && total == 12)
    }

    do {
      // Task 2: Guided modification
      let values = [2, -3, 4]
      var total = 0
      var kept: [Int] = []
      for value in values where value >= 0 {
        total += value
        kept.append(value)
        precondition(total == kept.reduce(0, +))
      }
      precondition(total == 6 && kept == [2, 4])
    }

    do {
      // Task 3: Independent construction
      func firstIndex(of target: Int, in values: [Int]) -> Int? {
        for (offset, value) in values.enumerated() where value == target {
          return offset
        }
        return nil
      }
      precondition(firstIndex(of: 7, in: [5, 7, 7]) == 1)
      precondition(firstIndex(of: 9, in: [5, 7]) == nil)
      precondition(firstIndex(of: 1, in: []) == nil)
    }

    do {
      // Task 4: Diagnose a defect
      let values = [3, 8, 8]
      var index = 0
      var steps = 0
      while index < values.count && values[index] != 8 {
        index += 1
        steps += 1
      }
      precondition(index == 1 && steps == 1)
    }

    do {
      // Task 5: Boundary evidence
      func firstOffset(of target: Int, in values: [Int]) -> Int? {
        for (offset, value) in values.enumerated() where value == target {
          return offset
        }
        return nil
      }
      precondition(firstOffset(of: 4, in: []) == nil)
      precondition(firstOffset(of: 4, in: [4]) == 0 && firstOffset(of: 9, in: [4]) == nil)
      precondition(firstOffset(of: 4, in: [1, 4, 4, 4]) == 1)
    }
    print("swift-007: passed")
  }
}
