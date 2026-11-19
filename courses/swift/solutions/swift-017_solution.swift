import Foundation

protocol Pricer { func cost(units: Int) -> Int }
struct FlatPrice: Pricer {
  let unit: Int
  func cost(units: Int) -> Int { unit * units }
}
struct CappedPrice: Pricer {
  let unit: Int
  let cap: Int
  func cost(units: Int) -> Int { min(unit * units, cap) }
}
protocol LabelFormatter {
  func label(for count: Int) -> String
}
struct PluralFormatter: LabelFormatter {
  func label(for count: Int) -> String { count == 1 ? "1 item" : "\(count) items" }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let price: any Pricer = FlatPrice(unit: 3)
      precondition(price.cost(units: 4) == 12)
    }

    do {
      let prices: [any Pricer] = [FlatPrice(unit: 3), CappedPrice(unit: 3, cap: 10)]
      precondition(prices.map { $0.cost(units: 4) } == [12, 10])
    }

    do {
      // Task 3: Independent construction
      let formatter: any LabelFormatter = PluralFormatter()
      precondition(formatter.label(for: 1) == "1 item")
      precondition(formatter.label(for: 3) == "3 items")
      precondition(formatter.label(for: 3) == formatter.label(for: 3))
    }
    print("swift-017: passed")
  }
}
