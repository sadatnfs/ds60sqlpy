import Foundation
import Observation
import JourneyCore

@MainActor
@Observable
final class PlanStore {
    private(set) var plan: StudyPlan
    var errorMessage: String?
    private(set) var persistenceBlocked = false
    private let file: URL

    init() {
        // UI tests deliberately get a disposable, separate app-owned directory.
        let testing = ProcessInfo.processInfo.arguments.contains("--ui-testing")
        let base = testing
            ? FileManager.default.temporaryDirectory.appendingPathComponent("JourneyUITestState", isDirectory: true)
            : FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
                .appendingPathComponent("JourneyLearningFixture", isDirectory: true)
        file = base.appendingPathComponent("plan.json")
        plan = try! StudyPlan() // An authored empty plan is always valid.
        if testing {
            plan = try! StudyPlan(items: [StudyItem(id: "fixture-read", title: "Read a chapter")])
            return
        }
        do {
            try FileManager.default.createDirectory(at: base, withIntermediateDirectories: true)
            if FileManager.default.fileExists(atPath: file.path) {
                plan = try StudyPlan.decode(Data(contentsOf: file))
            }
        } catch {
            // Keep the unreadable file intact. Never replace it with the empty default.
            persistenceBlocked = true
            errorMessage = "The saved plan could not be loaded. Its file was retained. \(error.localizedDescription)"
        }
    }

    func add(title: String) {
        do {
            var candidate = plan
            try candidate.add(StudyItem(id: UUID().uuidString, title: title))
            try commit(candidate)
        } catch {
            errorMessage = "The item was not saved. \(error.localizedDescription)"
        }
    }

    func update(id: String, title: String, completed: Bool) {
        do {
            var candidate = plan
            try candidate.update(id: id, title: title, completed: completed)
            try commit(candidate)
        } catch {
            errorMessage = "The change was not saved. \(error.localizedDescription)"
        }
    }

    private func commit(_ candidate: StudyPlan) throws {
        guard !persistenceBlocked else { throw StoreError.recoveryRequired }
        let directory = file.deletingLastPathComponent()
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        try candidate.encoded().write(to: file, options: .atomic)
        plan = candidate // Publish success only after the owned write succeeds.
        errorMessage = nil
    }

    enum StoreError: Error { case recoveryRequired }
}
