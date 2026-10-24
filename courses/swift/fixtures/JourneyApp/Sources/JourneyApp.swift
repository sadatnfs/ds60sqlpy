import SwiftUI

@main
struct JourneyApplication: App {
    @State private var store = PlanStore()

    var body: some Scene {
        WindowGroup {
            PlanView(store: store)
        }
    }
}
