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
    print("swift-003: passed")
  }
}
