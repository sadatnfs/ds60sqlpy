import XCTest

@MainActor
final class JourneySmokeTests: XCTestCase {
    func testAddItemUpdatesProgress() {
        let app = XCUIApplication()
        app.launchArguments = ["--ui-testing"]
        app.launch()
        let summary = app.staticTexts["progress-summary"]
        XCTAssertTrue(summary.waitForExistence(timeout: 10))
        XCTAssertEqual(summary.label, "0/1 complete")
        let title = app.textFields["new-item-title"]
        title.tap()
        title.typeText("Build an independent example")
        app.buttons["add-item"].tap()
        XCTAssertTrue(app.staticTexts["Build an independent example"].waitForExistence(timeout: 5))
        XCTAssertEqual(summary.label, "0/2 complete")
    }
}
