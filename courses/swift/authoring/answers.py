"""Reference answers for guide tasks, executed inside the lesson reference.

Each entry maps a lesson number to {task number: answer}. An answer has `code` (a
block run after the worked examples), optional file-scope `helpers`, `observe` (the
checked observation) and `explain`. Tasks without an entry are reported as having no
reference answer yet; `render.py` prints the coverage.
"""

ANSWERS = {
    1: {
        3: dict(
            code=r"""let shelves = 3
let booksPerShelf = 8
let capacity = shelves * booksPerShelf
precondition(capacity == 24)""",
            observe="Three shelves of eight books hold 24 books.",
            explain="The product is written as a calculation, and the precondition compares it with 24, a value worked out independently.",
        )
    },
    2: {
        3: dict(
            code=r"""let total = 7
let count = 2
let mean = Double(total) / Double(count)
precondition(mean == 3.5)
precondition(total / count == 3)""",
            observe="The mean is 3.5, while integer division of the same values would give 3.",
            explain="Converting both operands to Double before dividing is the deliberate step; dividing the Ints first would truncate the result.",
        )
    },
    3: {
        3: dict(
            code=r"""enum Addition: Equatable {
  case accepted(UInt8)
  case rejected
}
func add(_ left: UInt8, _ right: UInt8) -> Addition {
  let result = left.addingReportingOverflow(right)
  return result.overflow ? .rejected : .accepted(result.partialValue)
}
precondition(add(200, 50) == .accepted(250))
precondition(add(200, 56) == .rejected)""",
            observe="200 + 50 is accepted as 250; 200 + 56 is rejected instead of wrapping to 0.",
            explain="addingReportingOverflow exposes the overflow flag, and the enum gives the rejected outcome its own case rather than a sentinel number.",
        )
    },
    4: {
        3: dict(
            code=r"""func firstCharacter(_ text: String) -> Character? {
  text.first
}
precondition(firstCharacter("😀B") == "😀")
precondition(firstCharacter("") == nil)""",
            observe="The first Character of 😀B is 😀, and empty text gives nil.",
            explain="A Character is a full grapheme cluster, so the emoji is one element, and the optional result keeps empty text distinct from any character.",
        )
    },
    5: {
        3: dict(
            code=r"""func parseCount(_ text: String?) -> Int? {
  guard let text, let value = Int(text), value >= 0 else { return nil }
  return value
}
precondition(parseCount("12") == 12 && parseCount("0") == 0)
precondition(parseCount(nil) == nil && parseCount("-3") == nil)
precondition(parseCount("x") == nil)""",
            observe="12 and 0 are accepted; nil, -3 and x are rejected.",
            explain="One guard handles absence, non-numeric text and negative values, and a valid 0 is still returned as a value.",
        )
    },
    6: {
        3: dict(
            code=r"""func sign(_ quantity: Int) -> String {
  switch quantity {
  case ..<0: return "negative"
  case 0: return "zero"
  default: return "positive"
  }
}
precondition(sign(-2) == "negative" && sign(0) == "zero")
precondition(sign(7) == "positive")""",
            observe="-2, 0 and 7 are classified as negative, zero and positive.",
            explain="After the two explicit cases, only positive integers remain, so the default case is exactly the positive branch.",
        )
    },
    7: {
        3: dict(
            code=r"""func firstIndex(of target: Int, in values: [Int]) -> Int? {
  for (offset, value) in values.enumerated() where value == target {
    return offset
  }
  return nil
}
precondition(firstIndex(of: 7, in: [5, 7, 7]) == 1)
precondition(firstIndex(of: 9, in: [5, 7]) == nil)
precondition(firstIndex(of: 1, in: []) == nil)""",
            observe="The first 7 is at offset 1; a missing target and an empty array give nil.",
            explain="The loop returns at the first match, and nil keeps not-found separate from every valid offset.",
        )
    },
    8: {
        3: dict(
            code=r"""func normalized(_ quantity: Int, limit: Int) -> Int {
  min(max(quantity, 0), limit)
}
let requested = 15
precondition(normalized(requested, limit: 10) == 10)
precondition(normalized(-4, limit: 10) == 0 && requested == 15)""",
            observe="15 is normalized to 10 and -4 to 0, while the caller's value stays 15.",
            explain="The function takes its argument by value and returns a new result, so it cannot change the caller's variable.",
        )
    },
    9: {
        3: dict(
            code=r"""let source = [-1, 2, -3, 4]
let positives = source.filter { $0 > 0 }
precondition(positives == [2, 4])
precondition(source == [-1, 2, -3, 4])""",
            observe="The filtered array is [2, 4] and the source is unchanged.",
            explain="filter returns a new array; because arrays are values, the source keeps its own elements.",
        )
    },
    10: {
        3: dict(
            code=r"""let rows = ["pear", "apple", "pear", "", "fig"]
let names = Set(rows.filter { !$0.isEmpty }).sorted()
precondition(names == ["apple", "fig", "pear"])""",
            observe="The accepted names are apple, fig and pear, each once and sorted.",
            explain="Empty names are rejected first, the Set removes duplicates, and sorted() gives a stable order that does not depend on hashing.",
        )
    },
    11: {
        3: dict(
            code=r"""enum Load {
  case loading
  case ready(Int)
  case failed(String)
}
func label(_ state: Load) -> String {
  switch state {
  case .loading: return "loading"
  case .ready(let count): return "ready:\(count)"
  case .failed(let reason): return "failed:\(reason)"
  }
}
precondition(label(.loading) == "loading" && label(.ready(3)) == "ready:3")
precondition(label(.failed("offline")) == "failed:offline")""",
            observe="The states render as loading, ready:3 and failed:offline.",
            explain="Each case carries only the data that exists in that state, and the switch must handle all three.",
        )
    },
    12: {
        3: dict(
            code=r"""struct BoundedCounter {
  private(set) var value = 0
  let limit: Int
  mutating func increment() -> Bool {
    guard value < limit else { return false }
    value += 1
    return true
  }
}
var counter = BoundedCounter(limit: 2)
precondition(counter.increment() && counter.increment())
precondition(!counter.increment() && counter.value == 2)""",
            observe="Two increments succeed, the third is refused, and the value stays at 2.",
            explain="private(set) lets callers read value but change it only through increment, which enforces the limit.",
        )
    },
    13: {
        3: dict(
            code=r"""final class Coordinator {
  var openConnections = 0
}
struct Coordinate {
  var x: Int
  var y: Int
}
let shared = Coordinator()
let alias = shared
alias.openConnections += 1
let point = Coordinate(x: 1, y: 2)
var moved = point
moved.x = 5
precondition(shared.openConnections == 1 && shared === alias)
precondition(point.x == 1 && moved.x == 5)""",
            observe="Both coordinator references see 1 open connection, while moving the copied coordinate leaves the original at x = 1.",
            explain="A coordinator is shared state with one identity, so it is a class; a coordinate is a small value, so a struct copy is the right behavior.",
        )
    },
    14: {
        3: dict(
            code=r"""/// Stores meters only; feet is a derived view and is never stored.
struct Length {
  var meters: Double
  var feet: Double { meters / 0.3048 }
}
let length = Length(meters: 3.048)
precondition(abs(length.feet - 10) < 1e-9)""",
            observe="3.048 meters reads as 10 feet.",
            explain="With a single stored unit there is nothing to keep in sync; the converted value is computed from meters every time it is read.",
        )
    },
    15: {
        3: dict(
            code=r"""func transformAll(_ values: [Int], _ change: (Int) -> Int) -> [Int] {
  var result: [Int] = []
  for value in values { result.append(change(value)) }
  return result
}
let scaled = transformAll([1, 2, 3]) { $0 * 10 }
precondition(scaled == [10, 20, 30])""",
            observe="Applying the closure gives 10, 20 and 30.",
            explain="The caller supplies the behavior; the closure is non-escaping, so it runs only during the call.",
        )
    },
    16: {
        3: dict(
            code=r"""let result = importRows(["pear,2", "apple,3", "bad", "pear,1"])
var lines = result.counts.keys.sorted().map { "\($0): \(result.counts[$0]!)" }
lines.append("rejected: \(result.rejected)")
precondition(lines.joined(separator: "\n") == "apple: 3\npear: 3\nrejected: 1")""",
            observe="The report lists apple: 3, pear: 3 and rejected: 1.",
            explain="Sorting the keys makes the report deterministic, and the rejected count is reported beside the totals instead of being dropped.",
        )
    },
    17: {
        3: dict(
            helpers=r"""protocol LabelFormatter {
  func label(for count: Int) -> String
}
struct PluralFormatter: LabelFormatter {
  func label(for count: Int) -> String { count == 1 ? "1 item" : "\(count) items" }
}""",
            code=r"""let formatter: any LabelFormatter = PluralFormatter()
precondition(formatter.label(for: 1) == "1 item")
precondition(formatter.label(for: 3) == "3 items")
precondition(formatter.label(for: 3) == formatter.label(for: 3))""",
            observe="The formatter produces 1 item and 3 items, identically on every call.",
            explain="The protocol states the contract and the conforming type depends only on its input, so its labels are deterministic.",
        )
    },
    18: {
        3: dict(
            code=r"""struct Triple<T> {
  let first: T
  let second: T
  let third: T
  func rotated() -> Triple<T> { Triple(first: second, second: third, third: first) }
}
let rotated = Triple(first: 1, second: 2, third: 3).rotated()
precondition(rotated.first == 2 && rotated.second == 3 && rotated.third == 1)""",
            observe="Rotating (1, 2, 3) gives (2, 3, 1).",
            explain="The properties are let constants, so rotation returns a new triple instead of changing the original.",
        )
    },
    19: {
        3: dict(
            code=r"""func transformed<P: Producer>(_ producer: P, _ change: (P.Item) -> P.Item) -> P.Item {
  change(producer.produce())
}
let value: Int = transformed(IntegerSource()) { $0 + 1 }
precondition(value == 8)""",
            observe="Transforming the produced 7 gives 8, still an Int.",
            explain="The signature uses P.Item for both input and output, so the compiler guarantees the item type is preserved.",
        )
    },
    20: {
        3: dict(
            code=r"""func sum<S: Sequence>(_ values: S) -> S.Element where S.Element: AdditiveArithmetic {
  var total = S.Element.zero
  for value in values { total += value }
  return total
}
precondition(sum([1, 2, 3]) == 6)
precondition(sum([1.5, 2.5]) == 4.0)
precondition(sum([Int]()) == 0)""",
            observe="The sum works for Ints (6) and Doubles (4.0) and returns 0 for an empty sequence.",
            explain="AdditiveArithmetic supplies both .zero and +, which is exactly what summing needs, so any suitable element type works.",
        )
    },
    21: {
        3: dict(
            code=r"""struct Record {
  let name: String
  let quantity: Int
}
enum RecordError: Error, Equatable {
  case emptyName
  case negativeQuantity
}
func validate(_ record: Record) throws -> Record {
  guard !record.name.isEmpty else { throw RecordError.emptyName }
  guard record.quantity >= 0 else { throw RecordError.negativeQuantity }
  return record
}
let valid = try validate(Record(name: "pear", quantity: 2))
precondition(valid.quantity == 2)
var caught: RecordError? = nil
do {
  _ = try validate(Record(name: "", quantity: 1))
} catch let error as RecordError {
  caught = error
}
precondition(caught == .emptyName)""",
            observe="A valid record passes; an empty name throws RecordError.emptyName.",
            explain="Each rule throws its own error case, so the caller learns which rule failed instead of receiving a generic false.",
        )
    },
    22: {
        3: dict(
            code=r"""final class Listener {
  var events: [String] = []
}
final class Downloader {
  weak var delegate: Listener?
  func finish() { delegate?.events.append("finished") }
}
let downloader = Downloader()
var listener: Listener? = Listener()
downloader.delegate = listener
downloader.finish()
precondition(listener?.events == ["finished"])
listener = nil
precondition(downloader.delegate == nil)
downloader.finish()""",
            observe="The listener receives finished; after it is released the weak delegate becomes nil and finish() does nothing.",
            explain="The downloader does not own its delegate, so it cannot keep the listener alive or form a retain cycle with it.",
        )
    },
    23: {
        3: dict(
            code=r"""enum DecodeError: Error {
  case invalid
}
func trustedItem(from data: Data) throws -> Item {
  let item = try JSONDecoder().decode(Item.self, from: data)
  guard item.isValid else { throw DecodeError.invalid }
  return item
}
let good = try trustedItem(from: Data(#"{"name":"pear","quantity":2}"#.utf8))
precondition(good.quantity == 2)
var rejected = false
do {
  _ = try trustedItem(from: Data(#"{"name":"pear","quantity":-1}"#.utf8))
} catch DecodeError.invalid {
  rejected = true
}
precondition(rejected)""",
            observe="The valid item is returned; quantity -1 decodes but is rejected before it is trusted.",
            explain="Decoding proves only the shape; the validation step runs before the function returns, so callers never receive an invalid Item.",
        )
    },
    24: {
        3: dict(
            code=r"""struct Stock: Codable, Equatable {
  let name: String
  let quantity: Int
}
let manager = FileManager.default
let folder = manager.temporaryDirectory.appendingPathComponent(
  UUID().uuidString, isDirectory: true)
try manager.createDirectory(at: folder, withIntermediateDirectories: true)
defer { try? manager.removeItem(at: folder) }
let file = folder.appendingPathComponent("stock.json")
let saved = Stock(name: "pear", quantity: 3)
try JSONEncoder().encode(saved).write(to: file)
let restored = try JSONDecoder().decode(Stock.self, from: Data(contentsOf: file))
precondition(restored == saved && restored.quantity >= 0)""",
            observe="The value read back equals the saved one and passes the quantity check; the folder is removed at the end of the block.",
            explain="The folder is unique to this run, defer removes it on every exit path, and the decoded value is checked before use.",
        )
    },
    25: {
        3: dict(
            code=r"""let formatter = ISO8601DateFormatter()
let start = formatter.date(from: "2025-03-01T22:30:00Z")!
let end = formatter.date(from: "2025-03-02T01:15:00Z")!
let minutes = Int(end.timeIntervalSince(start) / 60)
let report = "\(minutes) minutes from \(formatter.string(from: start))"
precondition(report == "165 minutes from 2025-03-01T22:30:00Z")""",
            observe="The report reads 165 minutes from 2025-03-01T22:30:00Z.",
            explain="Fixed UTC fixtures make the duration independent of the machine's time zone, and the date change at midnight needs no special case.",
        )
    },
    28: {
        3: dict(
            code=r"""struct Quantity {
  let value: Int
}
func fetchRaw() async -> String { "12" }
func loadQuantity() async throws -> Quantity {
  let text = await fetchRaw()
  guard let value = Int(text), value >= 0 else { throw AsyncError.invalid }
  return Quantity(value: value)
}
let quantity = try await loadQuantity()
precondition(quantity.value == 12)""",
            observe="The adapter awaits the raw text and returns Quantity(value: 12).",
            explain="The adapter is the only place raw text becomes a domain value, and it validates after the suspension point, before returning.",
        )
    },
    29: {
        3: dict(
            code=r"""let inputs = [1, 2, 3, 4, 5]
let (results, peak) = await withTaskGroup(
  of: Int.self, returning: ([Int], Int).self
) { group in
  var next = 0
  var outstanding = 0
  var peak = 0
  var collected: [Int] = []
  while next < inputs.count && outstanding < 2 {
    let value = inputs[next]
    group.addTask { value * 10 }
    next += 1
    outstanding += 1
    peak = max(peak, outstanding)
  }
  while let finished = await group.next() {
    collected.append(finished)
    outstanding -= 1
    if next < inputs.count {
      let value = inputs[next]
      group.addTask { value * 10 }
      next += 1
      outstanding += 1
      peak = max(peak, outstanding)
    }
  }
  return (collected.sorted(), peak)
}
precondition(results == [10, 20, 30, 40, 50] && peak == 2)""",
            observe="All five inputs are processed, and at most two child tasks were ever outstanding.",
            explain="A new child is added only after group.next() returns a finished one, so admission is bounded by construction, not by timing.",
        )
    },
    30: {
        3: dict(
            code=r"""func process(_ items: [Int], isCancelled: () -> Bool) -> (done: [Int], cleanedUp: Bool) {
  var done: [Int] = []
  var cleanedUp = false
  do {
    defer { cleanedUp = true }
    for item in items {
      if isCancelled() { break }
      done.append(item)
    }
  }
  return (done, cleanedUp)
}
var checks = 0
let stopped = process([1, 2, 3, 4, 5]) {
  checks += 1
  return checks > 3
}
precondition(stopped.done == [1, 2, 3] && stopped.cleanedUp)
let task = Task { process([1, 2]) { Task.isCancelled } }
let full = await task.value
precondition(full.done == [1, 2] && full.cleanedUp)""",
            observe="When cancellation is observed before the fourth item, items 1 to 3 are done and cleanup still runs; an uncancelled task finishes both items.",
            explain="The loop is bounded by its input and checks for cancellation before each item; defer guarantees cleanup however the loop ends. Injecting the check keeps the test deterministic, and a real task passes Task.isCancelled.",
        )
    },
    31: {
        3: dict(
            code=r"""actor BoundedQueue {
  private var items: [Int] = []
  let capacity: Int
  init(capacity: Int) { self.capacity = capacity }
  func offer(_ item: Int) -> Bool {
    guard items.count < capacity else { return false }
    items.append(item)
    return true
  }
  func take() -> Int? { items.isEmpty ? nil : items.removeFirst() }
}
let queue = BoundedQueue(capacity: 2)
let admitted = [await queue.offer(1), await queue.offer(2), await queue.offer(3)]
precondition(admitted == [true, true, false])
let first = await queue.take()
precondition(first == 1)""",
            observe="Two offers are admitted, the third is refused, and the first item taken is 1.",
            explain="The actor serializes every offer and take, so the capacity check and the append can never interleave with another caller.",
        )
    },
    32: {
        3: dict(
            code=r"""actor ReceiptLedger {
  private var receipts: [String: Int] = [:]
  private(set) var executions = 0
  func apply(id: String, amount: Int) -> Int {
    if let receipt = receipts[id] { return receipt }
    executions += 1
    receipts[id] = amount
    return amount
  }
  func receipt(for id: String) -> Int? { receipts[id] }
}
let ledger = ReceiptLedger()
_ = await ledger.apply(id: "one", amount: 3)
let found = await ledger.receipt(for: "one")
let missing = await ledger.receipt(for: "two")
let executions = await ledger.executions
precondition(found == 3 && missing == nil && executions == 1)""",
            observe="The lookup finds receipt 3 for one, reports nil for two, and the work ran only once.",
            explain="receipt(for:) only reads stored results, so asking about an operation can never execute it again.",
        )
    },
    33: {
        3: dict(
            code=r"""struct Summary: Sendable {
  let count: Int
  let total: Int
}
let summary = await Task { () -> Summary in
  let values = [2, 3, 4]
  return Summary(count: values.count, total: values.reduce(0, +))
}.value
precondition(summary.count == 3 && summary.total == 9)""",
            observe="The task returns Summary(count: 3, total: 9).",
            explain="The result is an immutable Sendable value returned by the task, so no shared mutable object crosses the concurrency boundary.",
        )
    },
    34: {
        3: dict(
            code=r"""let (events, continuation) = AsyncStream<String>.makeStream()
let producer = Task {
  for name in ["start", "progress", "done"] { continuation.yield(name) }
  continuation.finish()
}
var received: [String] = []
for await event in events { received.append(event) }
await producer.value
precondition(received == ["start", "progress", "done"])""",
            observe="The consumer receives start, progress and done, and its loop ends.",
            explain="The producer owns the continuation and calls finish(); without it the consumer's for await would wait forever.",
        )
    },
    35: {
        3: dict(
            code=r"""/// Returns the sum of the values; the buffer pointer never escapes this call.
func total(of values: [Int]) -> Int {
  values.withUnsafeBufferPointer { buffer in
    var sum = 0
    for value in buffer { sum += value }
    return sum
  }
}
precondition(total(of: [2, 3, 4]) == 9 && total(of: []) == 0)""",
            observe="The safe wrapper returns 9 for [2, 3, 4] and 0 for an empty array.",
            explain="Callers see an ordinary function; the unsafe pointer exists only inside the closure and is read-only, so it cannot outlive the array.",
        )
    },
    36: {
        3: dict(
            code=r"""let names = ["pear", "apple", "fig"]
let queries = ["fig", "kiwi", "pear"]
let scanHits = queries.filter { names.contains($0) }.count
let index = Set(names)
let indexHits = queries.filter { index.contains($0) }.count
precondition(scanHits == 2 && indexHits == scanHits)""",
            observe="Both approaches find 2 of the 3 queries.",
            explain="The Set uses the same String equality as the scans, so it answers identically while replacing a linear search per query with one hash lookup.",
        )
    },
    37: {
        3: dict(
            helpers=r"""@propertyWrapper struct Trimmed {
  private var text = ""
  var wrappedValue: String {
    get { text }
    set { text = newValue.trimmingCharacters(in: .whitespaces) }
  }
  init(wrappedValue: String) { self.wrappedValue = wrappedValue }
}
struct DisplayLabel {
  @Trimmed var title = ""
}""",
            code=r"""var label = DisplayLabel()
label.title = "  Report  "
precondition(label.title == "Report")
precondition(DisplayLabel(title: " x ").title == "x")""",
            observe="Both assignment and initialization store the trimmed text Report and x.",
            explain="The wrapper applies one normalization policy in its setter, and init(wrappedValue:) routes initial values through the same setter.",
        )
    },
    38: {
        3: dict(
            code=r"""let hasWarnings = false
let report = sections {
  "Summary"
  "Totals"
  if hasWarnings { "Warnings" }
}
precondition(report == ["Summary", "Totals"])""",
            observe="The report contains Summary and Totals; the Warnings section is omitted.",
            explain="The builder turns each expression into a section and the if statement into an optional component, so the declaration reads like the report it builds.",
        )
    },
}
