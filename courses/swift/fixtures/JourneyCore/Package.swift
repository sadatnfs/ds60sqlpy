// swift-tools-version: 6.0
import PackageDescription

let package = Package(
  name: "JourneyCore",
  products: [
    .library(name: "JourneyCore", targets: ["JourneyCore"]),
    .executable(name: "journey-demo", targets: ["JourneyDemo"]),
  ],
  targets: [
    .target(name: "JourneyCore"),
    .executableTarget(name: "JourneyDemo", dependencies: ["JourneyCore"]),
    .testTarget(name: "JourneyCoreTests", dependencies: ["JourneyCore"]),
  ]
)
