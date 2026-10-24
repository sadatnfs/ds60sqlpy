import Foundation

enum QuantityError: Error { case invalid }
func parseQuantity(_ text: String) throws -> Int { guard let value = Int(text), value >= 0 else { throw QuantityError.invalid }; return value }

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
            switch outcome { case .success: preconditionFailure("invalid input accepted"); case .failure(let error): precondition(error is QuantityError) }
        }
        print("swift-021: passed")
    }
}
