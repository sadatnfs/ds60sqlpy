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

    do {
      // Task 1: Predict and explain
      var parent: Parent? = Parent()
      var child: Child? = Child()
      parent?.child = child
      child?.parent = parent
      weak var childObserver = child
      child = nil
      precondition(childObserver != nil)
      parent = nil
      precondition(childObserver == nil)
    }

    do {
      // Task 2: Guided modification
      var owner: Owner? = Owner()
      var second: Owner? = owner
      weak var observer = owner
      owner = nil
      precondition(observer != nil && second != nil)
      second = nil
      precondition(observer == nil)
    }

    do {
      // Task 3: Independent construction
      final class Listener {
        var events: [String] = []
      }
      final class Downloader {
        weak var delegate: Listener?
        func finish() { delegate?.events.append("finished") }
      }
      let downloader = Downloader()
      var listener: Listener? = Listener()
      downloader.delegate = listener
      downloader.finish()
      precondition(listener?.events == ["finished"])
      listener = nil
      precondition(downloader.delegate == nil)
      downloader.finish()
    }

    do {
      // Task 4: Diagnose a defect
      final class Ticker {
        var count = 0
        var onTick: (() -> Void)?
        func startStrong() { onTick = { self.count += 1 } }
        func startWeak() { onTick = { [weak self] in self?.count += 1 } }
      }
      var leaky: Ticker? = Ticker()
      leaky?.startStrong()
      weak var leakObserver = leaky
      leaky = nil
      precondition(leakObserver != nil)
      leakObserver?.onTick = nil
      precondition(leakObserver == nil)
      var fixed: Ticker? = Ticker()
      fixed?.startWeak()
      weak var fixedObserver = fixed
      fixed = nil
      precondition(fixedObserver == nil)
    }

    do {
      // Task 5: Boundary evidence
      final class Screen {
        var shown: [String] = []
      }
      var screen: Screen? = Screen()
      let show = { [weak screen] (text: String) -> Bool in
        guard let screen else { return false }
        screen.shown.append(text)
        return true
      }
      precondition(show("first") && screen?.shown == ["first"])
      screen = nil
      precondition(!show("late"))
    }
    print("swift-022: passed")
  }
}
