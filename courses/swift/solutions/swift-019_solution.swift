import Foundation

protocol Producer {
  associatedtype Item
  func produce() -> Item
}
struct IntegerSource: Producer { func produce() -> Int { 7 } }
func read<P: Producer>(_ producer: P) -> P.Item { producer.produce() }
func makeLabels() -> some Sequence<String> { ["a", "b"] }
func makeNoLabels() -> some Sequence<String> { [String]() }

@main
struct LessonMain {
  static func main() async throws {
    do {
      let source = IntegerSource()
      let value: Int = read(source)
      precondition(value == 7)
    }

    do {
      let labels = makeLabels()
      precondition(Array(labels) == ["a", "b"])
    }

    do {
      // Task 1: Predict and explain
      let produced = read(IntegerSource())
      precondition(type(of: produced) == Int.self)
      let doubled = produced * 2
      precondition(doubled == 14)
    }

    do {
      // Task 2: Guided modification
      struct NameSource: Producer {
        func produce() -> String { "pear" }
      }
      let name = read(NameSource())
      precondition(name.uppercased() == "PEAR")
      precondition(read(IntegerSource()) == 7)
    }

    do {
      // Task 3: Independent construction
      func transformed<P: Producer>(_ producer: P, _ change: (P.Item) -> P.Item) -> P.Item {
        change(producer.produce())
      }
      let value: Int = transformed(IntegerSource()) { $0 + 1 }
      precondition(value == 8)
    }

    do {
      // Task 5: Boundary evidence
      precondition(Array(makeNoLabels()).isEmpty)
      var count = 0
      for _ in makeLabels() { count += 1 }
      precondition(count == 2)
    }
    print("swift-019: passed")
  }
}
