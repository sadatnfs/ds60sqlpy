import Foundation

final class Owner {}
final class Parent { var child: Child? }
final class Child { weak var parent: Parent? }

@main
struct LessonMain {
  static func main() async throws {
    do {
      var owner: Owner? = Owner()
      weak var observer = owner
      precondition(observer != nil)
      owner = nil
      precondition(observer == nil)
    }

    do {
      var parent: Parent? = Parent()
      let child = Child()
      parent?.child = child
      child.parent = parent
      weak var observed = parent
      parent = nil
      precondition(observed == nil && child.parent == nil)
    }
    print("swift-022: passed")
  }
}
