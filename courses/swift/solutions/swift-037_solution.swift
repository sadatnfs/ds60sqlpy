import Foundation

@propertyWrapper struct Clamped { private var value: Int; let range: ClosedRange<Int>; init(wrappedValue: Int, _ range: ClosedRange<Int>) { self.range = range; self.value = min(max(wrappedValue, range.lowerBound), range.upperBound) }; var wrappedValue: Int { get { value } set { value = min(max(newValue, range.lowerBound), range.upperBound) } }; var projectedValue: ClosedRange<Int> { range } }
struct Control { @Clamped(0...10) var level = 0 }

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
        print("swift-037: passed")
    }
}
