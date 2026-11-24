import Foundation

struct Rectangle {
  var width: Int
  var height: Int
  var area: Int { width * height }
}
struct Temperature {
  var celsius: Double
  var fahrenheit: Double {
    get { celsius * 9 / 5 + 32 }
    set { celsius = (newValue - 32) * 5 / 9 }
  }
}
extension Rectangle {
  var perimeter: Int { 2 * (width + height) }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var rectangle = Rectangle(width: 3, height: 4)
      precondition(rectangle.area == 12)
      rectangle.width = 5
      precondition(rectangle.area == 20)
    }

    do {
      var temperature = Temperature(celsius: 0)
      precondition(temperature.fahrenheit == 32)
      temperature.fahrenheit = 212
      precondition(abs(temperature.celsius - 100) < 1e-9)
    }

    do {
      // Task 1: Predict and explain
      let rectangleFields = Mirror(reflecting: Rectangle(width: 3, height: 4)).children
      precondition(rectangleFields.map(\.label) == ["width", "height"])
      let temperatureFields = Mirror(reflecting: Temperature(celsius: 0)).children
      precondition(temperatureFields.map(\.label) == ["celsius"])
    }

    do {
      // Task 2: Guided modification
      var rectangle = Rectangle(width: 3, height: 4)
      precondition(rectangle.perimeter == 14)
      rectangle.width = 5
      precondition(rectangle.perimeter == 18)
    }

    do {
      // Task 3: Independent construction
      /// Stores meters only; feet is a derived view and is never stored.
      struct Length {
        var meters: Double
        var feet: Double { meters / 0.3048 }
      }
      let length = Length(meters: 3.048)
      precondition(abs(length.feet - 10) < 1e-9)
    }

    do {
      // Task 4: Diagnose a defect
      struct StaleRectangle {
        var width: Int
        var height: Int
        var area: Int
      }
      var stale = StaleRectangle(width: 3, height: 4, area: 12)
      stale.width = 5
      precondition(stale.area == 12)
      var derived = Rectangle(width: 3, height: 4)
      derived.width = 5
      precondition(derived.area == 20)
    }

    do {
      // Task 5: Boundary evidence
      precondition(Rectangle(width: 0, height: 4).area == 0)
      var temperature = Temperature(celsius: 0)
      precondition(temperature.fahrenheit == 32)
      temperature.celsius = 37.5
      precondition(abs(temperature.fahrenheit - 99.5) < 1e-9)
      temperature.fahrenheit = 98.6
      precondition(abs(temperature.celsius - 37) < 1e-9)
    }
    print("swift-014: passed")
  }
}
