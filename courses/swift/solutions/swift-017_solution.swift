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
    print("swift-017: passed")
  }
}
