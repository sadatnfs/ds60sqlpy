import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let result = UInt8.max.addingReportingOverflow(1)
      precondition(result.overflow)
      precondition(result.partialValue == 0)
      precondition(UInt8(2).addingReportingOverflow(3).partialValue == 5)
    }

    do {
      let actual = 0.1 + 0.2
      precondition(abs(actual - 0.3) < 1e-12)
      let exact = Decimal(string: "0.1")! + Decimal(string: "0.2")!
      precondition(exact == Decimal(string: "0.3")!)
    }

    do {
      // Task 1: Predict and explain
      precondition(UInt8.max == 255)
      let result = UInt8.max.addingReportingOverflow(1)
      precondition(result.overflow == true)
      precondition(result.partialValue == 0)
    }

    do {
      // Task 2: Guided modification
      let result = UInt8(0).subtractingReportingOverflow(1)
      precondition(result.overflow)
      precondition(result.partialValue == 255)
      precondition(UInt8(1).subtractingReportingOverflow(1).partialValue == 0)
    }

    do {
      // Task 3: Independent construction
      enum Addition: Equatable {
        case accepted(UInt8)
        case rejected
      }
      func add(_ left: UInt8, _ right: UInt8) -> Addition {
        let result = left.addingReportingOverflow(right)
        return result.overflow ? .rejected : .accepted(result.partialValue)
      }
      precondition(add(200, 50) == .accepted(250))
      precondition(add(200, 56) == .rejected)
    }

    do {
      // Task 4: Diagnose a defect
      let ignored = UInt8(250).addingReportingOverflow(10).partialValue
      precondition(ignored == 4)
      let checked = UInt8(250).addingReportingOverflow(10)
      precondition(checked.overflow && checked.partialValue == ignored)
    }

    do {
      // Task 5: Boundary evidence
      func checkedAdd(_ left: UInt8, _ right: UInt8) -> UInt8? {
        let result = left.addingReportingOverflow(right)
        return result.overflow ? nil : result.partialValue
      }
      precondition(checkedAdd(0, 0) == 0)
      precondition(checkedAdd(100, 55) == 155)
      precondition(checkedAdd(255, 0) == 255)
      precondition(checkedAdd(255, 1) == nil)
    }
    print("swift-003: passed")
  }
}
