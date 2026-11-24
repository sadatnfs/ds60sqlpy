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
      // Task 1: Predict and explain
      let greeting = "Hello, Swift"
      let letters = "Hello".count + "Swift".count
      precondition(letters == 10)
      precondition(greeting.count == letters + 2)
    }

    do {
      // Task 2: Guided modification
      let greeting = "Good morning"
      let words = greeting.split(separator: " ")
      precondition(words.map(\.count) == [4, 7])
      precondition(greeting.count == 4 + 1 + 7)
    }

    do {
      // Task 3: Independent construction
      let shelves = 3
      let booksPerShelf = 8
      let capacity = shelves * booksPerShelf
      precondition(capacity == 24)
    }

    do {
      // Task 5: Boundary evidence
      let booksPerShelf = 8
      func capacity(shelves: Int) -> Int { shelves * booksPerShelf }
      precondition(capacity(shelves: 0) == 0)
      precondition(capacity(shelves: 1) == 8)
      precondition(capacity(shelves: 1) != 1 + booksPerShelf)
    }
    print("swift-001: passed")
  }
}
