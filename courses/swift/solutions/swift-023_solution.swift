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
    print("swift-023: passed")
  }
}
