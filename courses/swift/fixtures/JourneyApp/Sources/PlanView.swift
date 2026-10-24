import JourneyCore
import SwiftUI

struct PlanView: View {
  @Bindable var store: PlanStore
  @State private var draftTitle = ""

  var body: some View {
    NavigationStack {
      VStack(alignment: .leading, spacing: 16) {
        Text("\(store.plan.completedCount)/\(store.plan.items.count) complete")
          .accessibilityIdentifier("progress-summary")
        HStack {
          TextField("New study item", text: $draftTitle)
            .accessibilityIdentifier("new-item-title")
            .textFieldStyle(.roundedBorder)
          Button("Add") {
            store.add(title: draftTitle)
            if store.errorMessage == nil { draftTitle = "" }
          }
          .accessibilityIdentifier("add-item")
          .disabled(
            draftTitle.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
              || store.persistenceBlocked)
        }
        if let error = store.errorMessage {
          Text(error).foregroundStyle(.red)
            .accessibilityIdentifier("save-error")
        }
        List(store.plan.items) { item in
          NavigationLink(value: item.id) {
            HStack {
              Image(systemName: item.completed ? "checkmark.circle.fill" : "circle")
                .accessibilityHidden(true)
              Text(item.title)
              Spacer()
              Text(item.completed ? "Complete" : "Incomplete")
                .font(.caption)
            }
          }
          .accessibilityLabel("\(item.title), \(item.completed ? "complete" : "incomplete")")
        }
        SelectableText(text: "State belongs to the model. Views describe its current value.")
          .frame(minHeight: 44)
      }
      .padding()
      .navigationTitle("Study journey")
      .navigationDestination(for: String.self) { id in
        if let item = store.plan.items.first(where: { $0.id == id }) {
          ItemEditor(store: store, item: item)
        } else {
          ContentUnavailableView("Item unavailable", systemImage: "questionmark.folder")
        }
      }
    }
  }
}

struct ItemEditor: View {
  let store: PlanStore
  let item: StudyItem
  @State private var title: String
  @State private var completed: Bool
  @Environment(\.dismiss) private var dismiss

  init(store: PlanStore, item: StudyItem) {
    self.store = store
    self.item = item
    _title = State(initialValue: item.title)
    _completed = State(initialValue: item.completed)
  }

  var body: some View {
    Form {
      TextField("Title", text: $title)
      Toggle("Completed", isOn: $completed)
      if let error = store.errorMessage { Text(error).foregroundStyle(.red) }
      Button("Save changes") {
        store.update(id: item.id, title: title, completed: completed)
        if store.errorMessage == nil { dismiss() }
      }
      .disabled(
        title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || store.persistenceBlocked)
      Button("Cancel") { dismiss() }
    }
    .navigationTitle("Edit study item")
  }
}
