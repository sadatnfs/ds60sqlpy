import Foundation

@propertyWrapper struct Clamped {
  private var value: Int
  let range: ClosedRange<Int>
  init(wrappedValue: Int, _ range: ClosedRange<Int>) {
    self.range = range
    self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
  }
  var wrappedValue: Int {
    get { value }
    set { value = min(max(newValue, range.lowerBound), range.upperBound) }
  }
  var projectedValue: ClosedRange<Int> { range }
}
struct Control { @Clamped(0...10) var level = 0 }
@propertyWrapper struct Trimmed {
  private var text = ""
  var wrappedValue: String {
    get { text }
    set { text = newValue.trimmingCharacters(in: .whitespaces) }
  }
  init(wrappedValue: String) { self.wrappedValue = wrappedValue }
}
struct DisplayLabel {
  @Trimmed var title = ""
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var control = Control()
      control.level = 12
      precondition(control.level == 10)
      control.level = -2
      precondition(control.level == 0)
    }

    do {
      var control = Control()
      control.level = 4
      precondition(control.level == 4)
      precondition(control.$level == 0...10)
    }

    do {
      // Task 1: Predict and explain
      let direct = Clamped(wrappedValue: 15, 0...10)
      precondition(direct.wrappedValue == 10)
      var control = Control()
      precondition(control.level == 0)
      control.level = 12
      precondition(control.level == 10)
      control.level = -2
      precondition(control.level == 0)
    }

    do {
      // Task 2: Guided modification
      struct Volume {
        @Clamped(1...5) var level = 3
      }
      var volume = Volume()
      volume.level = 0
      precondition(volume.level == 1)
      volume.level = 6
      precondition(volume.level == 5)
      precondition(volume.$level == 1...5)
    }

    do {
      // Task 3: Independent construction
      var label = DisplayLabel()
      label.title = "  Report  "
      precondition(label.title == "Report")
      precondition(DisplayLabel(title: " x ").title == "x")
    }

    do {
      // Task 4: Diagnose a defect
      struct Payment {
        @Clamped(0...100) var amount = 0
      }
      var payment = Payment()
      payment.amount = 250
      precondition(payment.amount == 100)
      enum AmountError: Error { case outOfRange }
      func checkedAmount(_ value: Int) throws -> Int {
        guard (0...100).contains(value) else { throw AmountError.outOfRange }
        return value
      }
      precondition((try? checkedAmount(250)) == nil)
    }

    do {
      // Task 5: Boundary evidence
      var control = Control()
      control.level = 0
      precondition(control.level == 0)
      control.level = 10
      precondition(control.level == 10)
      control.level = -1
      precondition(control.level == 0)
      control.level = 11
      precondition(control.level == 10)
    }
    print("swift-037: passed")
  }
}
