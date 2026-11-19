import Foundation

enum AsyncError: Error { case invalid }

@main
struct LessonMain {
  static func main() async throws {
    do {
      func double(_ value: Int) async -> Int { value * 2 }
      let result = await double(4)
      precondition(result == 8)
    }

    do {
      func validated(_ value: Int) async throws -> Int {
        guard value >= 0 else { throw AsyncError.invalid }
        return value
      }
      let accepted = try await validated(3)
      precondition(accepted == 3)
      var rejected = false
      do { _ = try await validated(-1) } catch AsyncError.invalid { rejected = true }
      precondition(rejected)
    }

    do {
      // Task 3: Independent construction
      struct Quantity {
        let value: Int
      }
      func fetchRaw() async -> String { "12" }
      func loadQuantity() async throws -> Quantity {
        let text = await fetchRaw()
        guard let value = Int(text), value >= 0 else { throw AsyncError.invalid }
        return Quantity(value: value)
      }
      let quantity = try await loadQuantity()
      precondition(quantity.value == 12)
    }
    print("swift-028: passed")
  }
}
