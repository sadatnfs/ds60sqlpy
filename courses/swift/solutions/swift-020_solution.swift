import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [10, 20, 30, 40]
      let slice = values[1...2]
      precondition(slice.startIndex == 1)
      precondition(slice.map { $0 / 10 } == [2, 3])
    }

    do {
      let transformed = [1, 2, 3].lazy.filter { $0 > 1 }.map { $0 * 10 }
      precondition(Array(transformed) == [20, 30])
      precondition([Int]().reduce(0, +) == 0)
    }

    do {
      // Task 1: Predict and explain
      let values = [10, 20, 30, 40]
      let slice = values[1...2]
      precondition(slice.count == 2)
      precondition(slice.startIndex == 1 && slice.endIndex == 3)
    }

    do {
      // Task 2: Guided modification
      let values = [10, 20, 30, 40]
      let slice = values[1...2]
      var seen: [Int] = []
      for index in slice.indices { seen.append(slice[index]) }
      precondition(seen == [20, 30])
      precondition(Array(slice.indices) == [1, 2])
    }

    do {
      // Task 3: Independent construction
      func sum<S: Sequence>(_ values: S) -> S.Element where S.Element: AdditiveArithmetic {
        var total = S.Element.zero
        for value in values { total += value }
        return total
      }
      precondition(sum([1, 2, 3]) == 6)
      precondition(sum([1.5, 2.5]) == 4.0)
      precondition(sum([Int]()) == 0)
    }

    do {
      // Task 4: Diagnose a defect
      let values = [10, 20, 30, 40]
      let slice = values[1...2]
      precondition(!slice.indices.contains(0))
      var total = 0
      for offset in 0..<slice.count {
        total += slice[slice.index(slice.startIndex, offsetBy: offset)]
      }
      precondition(total == 50)
    }

    do {
      // Task 5: Boundary evidence
      let empty = [1, 2, 3][3..<3]
      precondition(empty.isEmpty && empty.startIndex == 3)
      final class OneShot: Sequence, IteratorProtocol {
        var remaining: [Int]
        init(_ values: [Int]) { remaining = values }
        func next() -> Int? { remaining.isEmpty ? nil : remaining.removeFirst() }
      }
      let stream = OneShot([1, 2])
      precondition(Array(stream) == [1, 2])
      precondition(Array(stream).isEmpty)
    }
    print("swift-020: passed")
  }
}
