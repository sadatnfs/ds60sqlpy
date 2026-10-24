import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let greeting = "Hello, Swift"
      precondition(greeting.count == 12)
      print(greeting)
    }

    do {
      let rows = 4
      let seatsPerRow = 6
      let seats = rows * seatsPerRow
      precondition(seats == 24)
      precondition(seats != rows + seatsPerRow)
    }
    print("swift-001: passed")
  }
}
