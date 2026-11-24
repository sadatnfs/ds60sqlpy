import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [2, 4, 6, 8]
      var comparisons = 0
      for value in values {
        comparisons += 1
        if value == 8 { break }
      }
      precondition(comparisons == 4)
    }

    do {
      let index = Set([2, 4, 6, 8])
      precondition(index.contains(8) && !index.contains(9))
      precondition(index.count == 4)
    }

    do {
      // Task 1: Predict and explain
      func comparisons(_ values: [Int], _ target: Int) -> Int {
        var count = 0
        for value in values {
          count += 1
          if value == target { break }
        }
        return count
      }
      let values = [2, 4, 6, 8]
      precondition(comparisons(values, 2) == 1)
      precondition(comparisons(values, 8) == 4)
      precondition(comparisons(values, 9) == 4)
    }

    do {
      // Task 2: Guided modification
      func worstCase(_ values: [Int]) -> Int {
        var count = 0
        for value in values {
          count += 1
          if value == -1 { break }
        }
        return count
      }
      let small = [2, 4, 6, 8]
      let large = small + [10, 12, 14, 16]
      precondition(worstCase(small) == 4 && worstCase(large) == 8)
    }

    do {
      // Task 3: Independent construction
      let names = ["pear", "apple", "fig"]
      let queries = ["fig", "kiwi", "pear"]
      let scanHits = queries.filter { names.contains($0) }.count
      let index = Set(names)
      let indexHits = queries.filter { index.contains($0) }.count
      precondition(scanHits == 2 && indexHits == scanHits)
    }

    do {
      // Task 4: Diagnose a defect
      let values = Array(1...1000)
      var scanWork = 0
      for value in values {
        scanWork += 1
        if value == 3 { break }
      }
      let index = Set(values)
      let buildWork = values.count
      precondition(index.contains(3) && scanWork == 3 && buildWork == 1000)
    }

    do {
      // Task 5: Boundary evidence
      let duplicates = [2, 2, 4]
      precondition(Set(duplicates).count == 2 && duplicates.count == 3)
      precondition(Set(duplicates).contains(2))
      let empty: [Int] = []
      precondition(!empty.contains(1) && Set(empty).isEmpty)
    }
    print("swift-036: passed")
  }
}
