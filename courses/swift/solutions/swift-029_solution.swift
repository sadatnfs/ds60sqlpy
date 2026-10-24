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
    print("swift-029: passed")
  }
}
