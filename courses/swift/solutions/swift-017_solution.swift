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
      // Task 1: Predict and explain
      let prices: [any Pricer] = [FlatPrice(unit: 3), CappedPrice(unit: 3, cap: 10)]
      precondition(type(of: prices[0]) == FlatPrice.self)
      precondition(type(of: prices[1]) == CappedPrice.self)
      precondition(prices[0].cost(units: 4) == 3 * 4)
      precondition(prices[1].cost(units: 4) == min(3 * 4, 10))
    }

    do {
      // Task 2: Guided modification
      func totals(_ prices: [any Pricer], units: Int) -> [Int] {
        prices.map { $0.cost(units: units) }
      }
      let prices: [any Pricer] = [
        FlatPrice(unit: 3), CappedPrice(unit: 3, cap: 10), FlatPrice(unit: 5),
      ]
      precondition(totals(prices, units: 4) == [12, 10, 20])
    }

    do {
      // Task 3: Independent construction
      let formatter: any LabelFormatter = PluralFormatter()
      precondition(formatter.label(for: 1) == "1 item")
      precondition(formatter.label(for: 3) == "3 items")
      precondition(formatter.label(for: 3) == formatter.label(for: 3))
    }

    do {
      // Task 4: Diagnose a defect
      struct DollarPrice: Pricer {
        let dollars: Int
        func cost(units: Int) -> Int { dollars * units }
      }
      let cents: any Pricer = FlatPrice(unit: 300)
      let dollars: any Pricer = DollarPrice(dollars: 3)
      precondition(cents.cost(units: 2) == 600 && dollars.cost(units: 2) == 6)
      let fixed: any Pricer = FlatPrice(unit: 3 * 100)
      precondition(fixed.cost(units: 2) == cents.cost(units: 2))
    }

    do {
      // Task 5: Boundary evidence
      let capped = CappedPrice(unit: 3, cap: 12)
      precondition(capped.cost(units: 0) == 0)
      precondition(capped.cost(units: 4) == 12)
      precondition(capped.cost(units: 5) == 12)
      precondition(FlatPrice(unit: 3).cost(units: 0) == 0)
    }
    print("swift-017: passed")
  }
}
