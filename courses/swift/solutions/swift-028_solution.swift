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
      // Task 1: Predict and explain
      func square(_ value: Int) async -> Int { value * value }
      let first = await square(2)
      let second = await square(3)
      precondition(first + second == 13)
      async let left = square(4)
      async let right = square(5)
      let both = await left + right
      precondition(both == 41)
    }

    do {
      // Task 2: Guided modification
      func double(_ value: Int) async -> Int { value * 2 }
      let once = await double(4)
      let twice = await double(once)
      precondition(once == 8 && twice == 16)
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

    do {
      // Task 5: Boundary evidence
      func validated(_ value: Int) async throws -> Int {
        guard value >= 0 else { throw AsyncError.invalid }
        return value
      }
      let zero = try await validated(0)
      precondition(zero == 0)
      var failed = false
      do { _ = try await validated(-5) } catch AsyncError.invalid { failed = true }
      precondition(failed)
    }
    print("swift-028: passed")
  }
}
