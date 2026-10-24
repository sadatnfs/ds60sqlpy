import Foundation
import XCTest

@testable import JourneyCore

final class PlanTests: XCTestCase {
  func testRoundTripAndValueCopy() throws {
    let original = try StudyPlan(items: [StudyItem(id: "one", title: "Read")])
    var changed = original
    try changed.update(id: "one", title: "Read", completed: true)
    XCTAssertEqual(original.completedCount, 0)
    XCTAssertEqual(changed.completedCount, 1)
    XCTAssertEqual(try StudyPlan.decode(changed.encoded()), changed)
  }

  func testInvalidAdmissionPreservesState() throws {
    var plan = try StudyPlan(items: [StudyItem(id: "one", title: "Read")])
    let before = plan
    XCTAssertThrowsError(try plan.add(StudyItem(id: "one", title: "Duplicate"))) { error in
      XCTAssertEqual(error as? PlanError, .duplicateIdentity)
    }
    XCTAssertEqual(plan, before)
    XCTAssertThrowsError(try plan.update(id: "one", title: "  ", completed: true))
    XCTAssertEqual(plan, before)
  }

  func testDecodedDataStillNeedsValidation() throws {
    let duplicate = Data(
      #"{"schemaVersion":1,"items":[{"id":"one","title":"A","completed":false},{"id":"one","title":"B","completed":true}]}"#
        .utf8)
    XCTAssertThrowsError(try StudyPlan.decode(duplicate)) { error in
      XCTAssertEqual(error as? PlanError, .duplicateIdentity)
    }
    let future = Data(#"{"schemaVersion":99,"items":[]}"#.utf8)
    XCTAssertThrowsError(try StudyPlan.decode(future)) { error in
      XCTAssertEqual(error as? PlanError, .unsupportedVersion)
    }
  }

  func testEmptyAndMissingIdentity() throws {
    var plan = try StudyPlan()
    XCTAssertEqual(plan.completedCount, 0)
    XCTAssertThrowsError(try plan.update(id: "missing", title: "Read", completed: true)) { error in
      XCTAssertEqual(error as? PlanError, .missingIdentity)
    }
    XCTAssertEqual(plan.items, [])
  }
}
