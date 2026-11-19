import Foundation

enum QuantityError: Error { case invalid }
func parseQuantity(_ text: String) throws -> Int {
  guard let value = Int(text), value >= 0 else { throw QuantityError.invalid }
  return value
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let parsed = try parseQuantity("3")
      precondition(parsed == 3)
      var rejected = false
      do { _ = try parseQuantity("-1") } catch QuantityError.invalid { rejected = true }
      precondition(rejected)
    }

    do {
      let outcome = Result { try parseQuantity("bad") }
      switch outcome {
      case .success: preconditionFailure("invalid input accepted")
      case .failure(let error): precondition(error is QuantityError)
      }
    }

    do {
      // Task 3: Independent construction
      struct Record {
        let name: String
        let quantity: Int
      }
      enum RecordError: Error, Equatable {
        case emptyName
        case negativeQuantity
      }
      func validate(_ record: Record) throws -> Record {
        guard !record.name.isEmpty else { throw RecordError.emptyName }
        guard record.quantity >= 0 else { throw RecordError.negativeQuantity }
        return record
      }
      let valid = try validate(Record(name: "pear", quantity: 2))
      precondition(valid.quantity == 2)
      var caught: RecordError? = nil
      do {
        _ = try validate(Record(name: "", quantity: 1))
      } catch let error as RecordError {
        caught = error
      }
      precondition(caught == .emptyName)
    }
    print("swift-021: passed")
  }
}
