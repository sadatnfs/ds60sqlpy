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
      // Task 1: Predict and explain
      func trace(_ text: String) -> String {
        do {
          let value = try parseQuantity(text)
          return "returned \(value)"
        } catch {
          return "threw"
        }
      }
      precondition(trace("3") == "returned 3")
      precondition(trace("-1") == "threw" && trace("x") == "threw")
    }

    do {
      // Task 2: Guided modification
      enum QuantityProblem: Error, Equatable {
        case malformed
        case negative
      }
      func strictQuantity(_ text: String) throws(QuantityProblem) -> Int {
        guard let value = Int(text) else { throw .malformed }
        guard value >= 0 else { throw .negative }
        return value
      }
      func problem(_ text: String) -> QuantityProblem? {
        do { _ = try strictQuantity(text) } catch { return error }
        return nil
      }
      precondition(problem("x") == .malformed && problem("-1") == .negative)
      precondition(problem("4") == nil)
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

    do {
      // Task 4: Diagnose a defect
      precondition((try? parseQuantity("x")) == nil)
      precondition((try? parseQuantity("-1")) == nil)
      let kept = Result { try parseQuantity("-1") }
      if case .failure(let error) = kept { precondition(error is QuantityError) }
    }

    do {
      // Task 5: Boundary evidence
      func accepts(_ text: String) -> Bool { (try? parseQuantity(text)) != nil }
      precondition(!accepts(""))
      let zero = try parseQuantity("0")
      precondition(zero == 0)
      precondition(!accepts("99999999999999999999"))
    }
    print("swift-021: passed")
  }
}
