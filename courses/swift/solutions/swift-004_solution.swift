import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let text = "é"
      precondition(text.count == 1)
      precondition(text.utf8.count == 2)
      let combined = "e\u{301}"
      precondition(combined.count == 1 && combined.utf8.count == 3)
    }

    do {
      let text = "A😀B"
      let firstEnd = text.index(after: text.startIndex)
      precondition(String(text[..<firstEnd]) == "A")
      precondition(String(text[firstEnd...]) == "😀B")
    }

    do {
      // Task 1: Predict and explain
      let precomposed = "\u{E9}"
      let combined = "e\u{301}"
      precondition(precomposed.count == 1 && combined.count == 1)
      precondition(precomposed.utf8.count == 2 && combined.utf8.count == 3)
      precondition(precomposed.unicodeScalars.count == 1 && combined.unicodeScalars.count == 2)
      precondition(precomposed == combined)
    }

    do {
      // Task 2: Guided modification
      let text = "\u{E9}😀"
      precondition(text.count == 2)
      precondition(text.utf8.count == 2 + 4)
      precondition(text.utf16.count == 1 + 2)
    }

    do {
      // Task 3: Independent construction
      func firstCharacter(_ text: String) -> Character? {
        text.first
      }
      precondition(firstCharacter("😀B") == "😀")
      precondition(firstCharacter("") == nil)
    }

    do {
      // Task 4: Diagnose a defect
      let text = "A😀B"
      let byteOffset = Array(text.utf8).firstIndex(of: UInt8(ascii: "B"))!
      precondition(byteOffset == 5)
      let index = text.firstIndex(of: "B")!
      precondition(text.distance(from: text.startIndex, to: index) == 2)
      precondition(text[index] == "B")
    }

    do {
      // Task 5: Boundary evidence
      let empty = ""
      precondition(empty.first == nil && empty.isEmpty)
      let flag = "🇺🇸"
      precondition(flag.count == 1 && flag.unicodeScalars.count == 2)
      precondition(flag.first == "🇺🇸")
      let family = "👨‍👩‍👧"
      precondition(family.count == 1 && family.unicodeScalars.count == 5)
    }
    print("swift-004: passed")
  }
}
