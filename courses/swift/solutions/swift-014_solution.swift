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
      // Task 3: Independent construction
      /// Stores meters only; feet is a derived view and is never stored.
      struct Length {
        var meters: Double
        var feet: Double { meters / 0.3048 }
      }
      let length = Length(meters: 3.048)
      precondition(abs(length.feet - 10) < 1e-9)
    }
    print("swift-014: passed")
  }
}
