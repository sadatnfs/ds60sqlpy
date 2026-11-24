import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let perBox = 4
      var total = 0
      total += perBox
      total += perBox
      precondition(total == 8 && perBox == 4)
    }

    do {
      let whole = 7 / 2
      let fractional = Double(7) / Double(2)
      precondition(whole == 3)
      precondition(fractional == 3.5)
    }

    do {
      // Task 1: Predict and explain
      let perBox = 4
      var total = 0
      total += perBox
      let whole = 7 / 2
      let fractional = Double(7) / Double(2)
      precondition(type(of: perBox) == Int.self && type(of: total) == Int.self)
      precondition(type(of: whole) == Int.self && type(of: fractional) == Double.self)
    }

    do {
      // Task 2: Guided modification
      let perBox = 4
      let boxes = 2
      let total = perBox * boxes
      precondition(total == 8 && perBox == 4)
    }

    do {
      // Task 3: Independent construction
      let total = 7
      let count = 2
      let mean = Double(total) / Double(count)
      precondition(mean == 3.5)
      precondition(total / count == 3)
    }

    do {
      // Task 4: Diagnose a defect
      let total = 7
      let count = 2
      let late = Double(total / count)
      let early = Double(total) / Double(count)
      precondition(late == 3.0)
      precondition(early == 3.5)
    }

    do {
      // Task 5: Boundary evidence
      func mean(_ total: Int, _ count: Int) -> Double { Double(total) / Double(count) }
      precondition(mean(8, 2) == 4.0 && 8 / 2 == 4)
      precondition(mean(7, 2) == 3.5 && 7 / 2 == 3)
    }
    print("swift-002: passed")
  }
}
