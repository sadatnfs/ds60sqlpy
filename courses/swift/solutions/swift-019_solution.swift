import Foundation

protocol Producer {
  associatedtype Item
  func produce() -> Item
}
struct IntegerSource: Producer { func produce() -> Int { 7 } }
func read<P: Producer>(_ producer: P) -> P.Item { producer.produce() }
func makeLabels() -> some Sequence<String> { ["a", "b"] }

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
      // Task 3: Independent construction
      func transformed<P: Producer>(_ producer: P, _ change: (P.Item) -> P.Item) -> P.Item {
        change(producer.produce())
      }
      let value: Int = transformed(IntegerSource()) { $0 + 1 }
      precondition(value == 8)
    }
    print("swift-019: passed")
  }
}
