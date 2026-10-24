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
    print("swift-019: passed")
  }
}
