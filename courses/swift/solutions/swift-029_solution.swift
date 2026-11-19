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
    print("swift-029: passed")
  }
}
