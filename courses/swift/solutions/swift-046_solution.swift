import Foundation



@main
struct LessonMain {
    static func main() async throws {
        do {
            let evidence: Set<String> = ["domain-tests", "package-build"]
            precondition(!evidence.contains("ui-tested"))
            precondition(!evidence.contains("device-signed"))
        }

        do {
            let required: Set<String> = ["domain-tests", "ui-smoke", "save-reload"]
            let observed: Set<String> = ["domain-tests", "ui-smoke"]
            precondition(required.subtracting(observed) == ["save-reload"])
        }
        print("swift-046: passed")
    }
}
