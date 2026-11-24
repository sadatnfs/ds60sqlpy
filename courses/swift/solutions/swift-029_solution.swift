import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = await withTaskGroup(of: Int.self, returning: [Int].self) { group in
        for value in [1, 2, 3] { group.addTask { value * 2 } }
        var results: [Int] = []
        for await result in group { results.append(result) }
        return results.sorted()
      }
      precondition(values == [2, 4, 6])
    }

    do {
      let count = await withTaskGroup(of: Int.self, returning: Int.self) { group in
        var total = 0
        for await value in group { total += value }
        return total
      }
      precondition(count == 0)
    }

    do {
      // Task 1: Predict and explain
      let values = await withTaskGroup(of: Int.self, returning: [Int].self) { group in
        for value in [1, 2, 3] { group.addTask { value * 2 } }
        var owned: [Int] = []
        for await result in group { owned.append(result) }
        return owned
      }
      precondition(values.count == 3 && values.sorted() == [2, 4, 6])
    }

    do {
      // Task 2: Guided modification
      let inputs = [3, 1, 2]
      let ordered = await withTaskGroup(of: (Int, Int).self, returning: [Int].self) { group in
        for (index, value) in inputs.enumerated() { group.addTask { (index, value * 2) } }
        var pairs: [(Int, Int)] = []
        for await pair in group { pairs.append(pair) }
        return pairs.sorted { $0.0 < $1.0 }.map { $0.1 }
      }
      precondition(ordered == [6, 2, 4])
    }

    do {
      // Task 3: Independent construction
      let inputs = [1, 2, 3, 4, 5]
      let (results, peak) = await withTaskGroup(
        of: Int.self, returning: ([Int], Int).self
      ) { group in
        var next = 0
        var outstanding = 0
        var peak = 0
        var collected: [Int] = []
        while next < inputs.count && outstanding < 2 {
          let value = inputs[next]
          group.addTask { value * 10 }
          next += 1
          outstanding += 1
          peak = max(peak, outstanding)
        }
        while let finished = await group.next() {
          collected.append(finished)
          outstanding -= 1
          if next < inputs.count {
            let value = inputs[next]
            group.addTask { value * 10 }
            next += 1
            outstanding += 1
            peak = max(peak, outstanding)
          }
        }
        return (collected.sorted(), peak)
      }
      precondition(results == [10, 20, 30, 40, 50] && peak == 2)
    }

    do {
      // Task 4: Diagnose a defect
      let doubled = await withTaskGroup(of: Int.self, returning: [Int].self) { group in
        for value in [4, 5] { group.addTask { value * 2 } }
        var results: [Int] = []
        for await result in group { results.append(result) }
        return results.sorted()
      }
      precondition(doubled == [8, 10])
    }

    do {
      // Task 5: Boundary evidence
      enum ChildError: Error { case failed }
      let empty = try await withThrowingTaskGroup(of: Int.self, returning: Int.self) { group in
        var total = 0
        for try await value in group { total += value }
        return total
      }
      precondition(empty == 0)
      var failed = false
      do {
        _ = try await withThrowingTaskGroup(of: Int.self, returning: Int.self) { group in
          for value in [1, 2, 3] {
            group.addTask {
              if value == 2 { throw ChildError.failed }
              return value
            }
          }
          var total = 0
          for try await value in group { total += value }
          return total
        }
      } catch ChildError.failed {
        failed = true
      }
      precondition(failed)
    }
    print("swift-029: passed")
  }
}
