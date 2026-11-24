import Foundation

struct LoadState {
  var generation: Int
  var title: String?
  mutating func accept(_ value: String, generation candidate: Int) {
    guard candidate == generation else { return }
    title = value
  }
}
struct TransportResponse: Sendable {
  let status: Int
  let body: Data
}
protocol TitleTransport: Sendable {
  func fetch(_ path: String) async throws -> TransportResponse
}
struct FakeTransport: TitleTransport {
  let responses: [String: TransportResponse]
  func fetch(_ path: String) async throws -> TransportResponse {
    guard let response = responses[path] else { throw TitleLoadError.unreachable }
    return response
  }
}
enum TitleLoadError: Error, Equatable {
  case status(Int)
  case emptyBody, unreachable
}
func loadTitle(_ path: String, using transport: some TitleTransport) async throws -> String {
  let response = try await transport.fetch(path)
  guard response.status == 200 else { throw TitleLoadError.status(response.status) }
  guard let text = String(data: response.body, encoding: .utf8), !text.isEmpty else {
    throw TitleLoadError.emptyBody
  }
  return text
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var state = LoadState(generation: 2, title: nil)
      state.accept("new", generation: 2)
      precondition(state.title == "new")
    }

    do {
      var state = LoadState(generation: 2, title: "new")
      state.accept("old", generation: 1)
      precondition(state.title == "new")
    }

    do {
      // Task 1: Predict and explain
      var state = LoadState(generation: 1, title: nil)
      state.generation += 1
      state.accept("first", generation: 1)
      precondition(state.title == nil)
      state.accept("second", generation: 2)
      precondition(state.title == "second")
    }

    do {
      // Task 2: Guided modification
      var state = LoadState(generation: 3, title: "three")
      state.generation = 4
      state.accept("late three", generation: 3)
      state.accept("four", generation: 4)
      precondition(state.title == "four")
    }

    do {
      // Task 3: Independent construction
      let fake = FakeTransport(responses: [
        "/ok": TransportResponse(status: 200, body: Data("Read".utf8)),
        "/down": TransportResponse(status: 503, body: Data()),
      ])
      let title = try await loadTitle("/ok", using: fake)
      precondition(title == "Read")
      var failure: TitleLoadError?
      do { _ = try await loadTitle("/down", using: fake) } catch let error as TitleLoadError {
        failure = error
      }
      precondition(failure == .status(503))
    }

    do {
      // Task 4: Diagnose a defect
      var state = LoadState(generation: 0, title: nil)
      state.generation = 1
      let oldQuery = state.generation
      state.generation = 2
      let newQuery = state.generation
      state.accept("results for re", generation: newQuery)
      state.accept("results for r", generation: oldQuery)
      precondition(state.title == "results for re")
    }

    do {
      // Task 5: Boundary evidence
      enum Outcome: Equatable {
        case title(String)
        case empty, malformed
        case status(Int)
      }
      func adapt(status: Int, body: Data) -> Outcome {
        guard status == 200 else { return .status(status) }
        guard !body.isEmpty else { return .empty }
        guard let text = String(data: body, encoding: .utf8) else { return .malformed }
        return .title(text)
      }
      precondition(adapt(status: 200, body: Data()) == .empty)
      precondition(adapt(status: 200, body: Data([0xFF, 0xFE])) == .malformed)
      precondition(adapt(status: 404, body: Data("x".utf8)) == .status(404))
      let task = Task { () -> Bool in
        do {
          try await Task.sleep(for: .seconds(30))
          return false
        } catch { return error is CancellationError }
      }
      task.cancel()
      let cancelled = await task.value
      precondition(cancelled)
    }
    print("swift-043: passed")
  }
}
