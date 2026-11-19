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

    do {
      // Task 3: Independent construction
      let shelves = 3
      let booksPerShelf = 8
      let capacity = shelves * booksPerShelf
      precondition(capacity == 24)
    }
    print("swift-001: passed")
  }
}
