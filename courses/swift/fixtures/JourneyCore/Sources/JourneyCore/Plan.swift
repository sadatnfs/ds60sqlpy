import Foundation

public struct StudyItem: Identifiable, Codable, Equatable, Sendable {
  public let id: String
  public var title: String
  public var completed: Bool

  public init(id: String, title: String, completed: Bool = false) throws {
    guard !id.isEmpty, !title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
      throw PlanError.invalidItem
    }
    self.id = id
    self.title = title
    self.completed = completed
  }
}

public enum PlanError: Error, Equatable {
  case invalidItem
  case duplicateIdentity
  case missingIdentity
  case unsupportedVersion
}

public struct StudyPlan: Codable, Equatable, Sendable {
  public let schemaVersion: Int
  public private(set) var items: [StudyItem]

  public init(items: [StudyItem] = []) throws {
    schemaVersion = 1
    self.items = items
    try validate()
  }

  public var completedCount: Int { items.filter(\.completed).count }

  public func validate() throws {
    guard schemaVersion == 1 else { throw PlanError.unsupportedVersion }
    guard
      items.allSatisfy({
        !$0.id.isEmpty && !$0.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
      })
    else {
      throw PlanError.invalidItem
    }
    guard Set(items.map(\.id)).count == items.count else { throw PlanError.duplicateIdentity }
  }

  public mutating func add(_ item: StudyItem) throws {
    var candidate = self
    candidate.items.append(item)
    try candidate.validate()
    self = candidate
  }

  public mutating func update(id: String, title: String, completed: Bool) throws {
    guard let index = items.firstIndex(where: { $0.id == id }) else {
      throw PlanError.missingIdentity
    }
    let replacement = try StudyItem(id: id, title: title, completed: completed)
    items[index] = replacement
  }

  public static func decode(_ data: Data) throws -> StudyPlan {
    let plan = try JSONDecoder().decode(StudyPlan.self, from: data)
    try plan.validate()
    return plan
  }

  public func encoded() throws -> Data {
    try validate()
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    return try encoder.encode(self)
  }
}
