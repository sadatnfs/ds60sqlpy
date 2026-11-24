import Foundation

struct Item: Codable, Equatable {
  let name: String
  let quantity: Int
  var isValid: Bool { !name.isEmpty && quantity >= 0 }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let original = Item(name: "pear", quantity: 3)
      let data = try JSONEncoder().encode(original)
      let restored = try JSONDecoder().decode(Item.self, from: data)
      precondition(restored == original)
    }

    do {
      let data = Data("{\"name\":\"pear\",\"quantity\":-2}".utf8)
      let decoded = try JSONDecoder().decode(Item.self, from: data)
      precondition(!decoded.isValid)
      precondition(!Item(name: "", quantity: 1).isValid)
    }

    do {
      // Task 1: Predict and explain
      let invalid = Item(name: "", quantity: -1)
      let data = try JSONEncoder().encode(invalid)
      let restored = try JSONDecoder().decode(Item.self, from: data)
      precondition(restored == invalid && !restored.isValid)
    }

    do {
      // Task 2: Guided modification
      struct Described: Codable, Equatable {
        let name: String
        let description: String?
      }
      let missing = try JSONDecoder().decode(
        Described.self, from: Data(#"{"name":"pear"}"#.utf8))
      precondition(missing.description == nil)
      let present = try JSONDecoder().decode(
        Described.self, from: Data(#"{"name":"pear","description":"ripe"}"#.utf8))
      precondition(present.description == "ripe")
    }

    do {
      // Task 3: Independent construction
      enum DecodeError: Error {
        case invalid
      }
      func trustedItem(from data: Data) throws -> Item {
        let item = try JSONDecoder().decode(Item.self, from: data)
        guard item.isValid else { throw DecodeError.invalid }
        return item
      }
      let good = try trustedItem(from: Data(#"{"name":"pear","quantity":2}"#.utf8))
      precondition(good.quantity == 2)
      var rejected = false
      do {
        _ = try trustedItem(from: Data(#"{"name":"pear","quantity":-1}"#.utf8))
      } catch DecodeError.invalid {
        rejected = true
      }
      precondition(rejected)
    }

    do {
      // Task 4: Diagnose a defect
      let data = Data(#"{"name":"","quantity":-5}"#.utf8)
      let decoded = try JSONDecoder().decode(Item.self, from: data)
      precondition(decoded.name.isEmpty && decoded.quantity == -5)
      precondition(!decoded.isValid)
    }

    do {
      // Task 5: Boundary evidence
      func decodes(_ json: String) -> Bool {
        (try? JSONDecoder().decode(Item.self, from: Data(json.utf8))) != nil
      }
      precondition(!decodes(#"{"name":"pear","#))
      precondition(!decodes(#"{"name":"pear"}"#))
      precondition(decodes(#"{"name":"pear","quantity":1,"color":"green"}"#))
    }
    print("swift-023: passed")
  }
}
