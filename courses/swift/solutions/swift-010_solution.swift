import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let counts = ["pear": 0]
      precondition(counts["pear"] == 0)
      precondition(counts["apple"] == nil)
    }

    do {
      var tags: Set<String> = ["red"]
      precondition(!tags.insert("red").inserted)
      precondition(tags.insert("blue").inserted)
      precondition(tags.sorted() == ["blue", "red"])
    }

    do {
      // Task 1: Predict and explain
      let counts = ["pear": 0]
      let pear: Int? = counts["pear"]
      let apple: Int? = counts["apple"]
      precondition(pear == .some(0))
      precondition(apple == .none)
      precondition(counts["apple", default: 0] == 0)
    }

    do {
      // Task 2: Guided modification
      let tags = ["red", "blue", "red", "red"]
      var counts: [String: Int] = [:]
      for tag in tags { counts[tag, default: 0] += 1 }
      precondition(counts == ["red": 3, "blue": 1])
    }

    do {
      // Task 3: Independent construction
      let rows = ["pear", "apple", "pear", "", "fig"]
      let names = Set(rows.filter { !$0.isEmpty }).sorted()
      precondition(names == ["apple", "fig", "pear"])
    }

    do {
      // Task 4: Diagnose a defect
      struct Product: Hashable {
        let sku: String
      }
      let product = Product(sku: "A-17")
      let storedKey = product.sku
      precondition(Product(sku: storedKey) == product)
      precondition(product.hashValue == Product(sku: "A-17").hashValue)
    }

    do {
      // Task 5: Boundary evidence
      var stock = ["pear": 0]
      precondition(stock["kiwi"] == nil && stock["pear"] == 0)
      stock["pear"] = 5
      precondition(stock.count == 1 && stock["pear"] == 5)
      let merged = Dictionary([("fig", 1), ("fig", 2)], uniquingKeysWith: +)
      precondition(merged == ["fig": 3])
    }
    print("swift-010: passed")
  }
}
