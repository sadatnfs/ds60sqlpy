"""Reference answers for guide tasks, executed inside the lesson reference.

Each entry maps a lesson number to {task number: answer}. An answer has `code` (a
block run after the worked examples), optional file-scope `helpers`, `observe` (the
checked observation) and `explain`; an entry without `code` is a written answer. The
`EXTRA` dict, merged into ANSWERS at the end, holds the task 1-5 answers added later.
Tasks without an entry are reported as having no reference answer yet; `render.py`
prints the coverage.
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

EXTRA = {
    1: {
        1: dict(
            code=r"""let greeting = "Hello, Swift"
let letters = "Hello".count + "Swift".count
precondition(letters == 10)
precondition(greeting.count == letters + 2)""",
            observe="Hello, Swift has 12 Characters: 10 letters plus the comma and the space.",
            explain="Counting the two words separately and adding the punctuation by hand gives a prediction that does not come from greeting.count itself, so the check can disagree with it.",
        ),
        2: dict(
            code=r"""let greeting = "Good morning"
let words = greeting.split(separator: " ")
precondition(words.map(\.count) == [4, 7])
precondition(greeting.count == 4 + 1 + 7)""",
            observe="Good morning splits into words of 4 and 7 Characters, and the whole greeting counts 12 with the space.",
            explain="The recount is built from the parts (two words and one separator), so changing the greeting text without recounting makes the final precondition fail instead of passing silently.",
        ),
        4: dict(
            explain="Deleting the brace that closes `static func main()` makes swiftc stop with a diagnostic such as `expected '}' in struct` pointing at the end of main.swift. That is a compilation failure: no program was produced, so Hello, Swift, the preconditions and the swift-001 marker never run. Record that first diagnostic, restore the brace, and confirm the marker returns; a failed precondition would instead report a file and line after execution had started.",
        ),
        5: dict(
            code=r"""let booksPerShelf = 8
func capacity(shelves: Int) -> Int { shelves * booksPerShelf }
precondition(capacity(shelves: 0) == 0)
precondition(capacity(shelves: 1) == 8)
precondition(capacity(shelves: 1) != 1 + booksPerShelf)""",
            observe="Zero shelves hold 0 books and one shelf holds 8, not the 9 that adding the dimensions would give.",
            explain="Zero is the identity edge of the multiplication and one shelf isolates the per-shelf amount, so the two cases catch a wrong operator that the three-shelf case alone could hide.",
        ),
    },
    2: {
        1: dict(
            code=r"""let perBox = 4
var total = 0
total += perBox
let whole = 7 / 2
let fractional = Double(7) / Double(2)
precondition(type(of: perBox) == Int.self && type(of: total) == Int.self)
precondition(type(of: whole) == Int.self && type(of: fractional) == Double.self)""",
            observe="perBox, total and whole are inferred as Int and fractional as Double.",
            explain="Integer literals default to Int, so 7 / 2 stays Int; the explicit Double conversions make the division and its result Double. type(of:) confirms the static choice at run time.",
        ),
        2: dict(
            code=r"""let perBox = 4
let boxes = 2
let total = perBox * boxes
precondition(total == 8 && perBox == 4)""",
            observe="Computing the total once as perBox * boxes gives 8 with every binding declared let.",
            explain="Example A needs var because += reassigns total twice. When the total is produced by one expression it is assigned exactly once, so let compiles, and swiftc's never-mutated warning disappears.",
        ),
        4: dict(
            code=r"""let total = 7
let count = 2
let late = Double(total / count)
let early = Double(total) / Double(count)
precondition(late == 3.0)
precondition(early == 3.5)""",
            observe="Converting after the division gives 3.0; converting the operands first gives 3.5.",
            explain="total / count is Int division and has already discarded the half before Double(...) sees it; the conversion must happen to the operands, not to the truncated quotient.",
        ),
        5: dict(
            code=r"""func mean(_ total: Int, _ count: Int) -> Double { Double(total) / Double(count) }
precondition(mean(8, 2) == 4.0 && 8 / 2 == 4)
precondition(mean(7, 2) == 3.5 && 7 / 2 == 3)""",
            observe="8 and 2 give 4.0 by both routes, while 7 and 2 give 3.5 only with the conversion (Int division gives 3).",
            explain="An exactly divisible pair cannot reveal truncation, so the non-divisible pair is the case that distinguishes the deliberate conversion from integer division.",
        ),
    },
    3: {
        1: dict(
            code=r"""precondition(UInt8.max == 255)
let result = UInt8.max.addingReportingOverflow(1)
precondition(result.overflow == true)
precondition(result.partialValue == 0)""",
            observe="UInt8.max is 255; adding 1 reports overflow true and partial value 0.",
            explain="256 needs a ninth bit, so the low eight bits are all zero; the reporting operation returns that wrapped value together with the flag instead of trapping.",
        ),
        2: dict(
            code=r"""let result = UInt8(0).subtractingReportingOverflow(1)
precondition(result.overflow)
precondition(result.partialValue == 255)
precondition(UInt8(1).subtractingReportingOverflow(1).partialValue == 0)""",
            observe="0 minus 1 reports overflow with partial value 255, while 1 minus 1 is 0 without overflow.",
            explain="An unsigned type has no -1, so the lower boundary wraps to the top of the range; the flag is the only signal that 255 is not a real difference.",
        ),
        4: dict(
            code=r"""let ignored = UInt8(250).addingReportingOverflow(10).partialValue
precondition(ignored == 4)
let checked = UInt8(250).addingReportingOverflow(10)
precondition(checked.overflow && checked.partialValue == ignored)""",
            observe="Reading only partialValue turns 250 + 10 into 4; the same result's overflow flag is true.",
            explain="260 minus 256 leaves 4, a plausible-looking quantity. Code that drops the flag reports it as a real total, so the flag must be checked before the partial value is used.",
        ),
        5: dict(
            code=r"""func checkedAdd(_ left: UInt8, _ right: UInt8) -> UInt8? {
  let result = left.addingReportingOverflow(right)
  return result.overflow ? nil : result.partialValue
}
precondition(checkedAdd(0, 0) == 0)
precondition(checkedAdd(100, 55) == 155)
precondition(checkedAdd(255, 0) == 255)
precondition(checkedAdd(255, 1) == nil)""",
            observe="0 + 0 is 0, 100 + 55 is 155, 255 + 0 is 255, and 255 + 1 is rejected as nil.",
            explain="The maximum itself is still a valid sum; only the step past 255 overflows, so testing 255 + 0 and 255 + 1 pins the boundary from both sides.",
        ),
    },
    4: {
        1: dict(
            code=r"""let precomposed = "\u{E9}"
let combined = "e\u{301}"
precondition(precomposed.count == 1 && combined.count == 1)
precondition(precomposed.utf8.count == 2 && combined.utf8.count == 3)
precondition(precomposed.unicodeScalars.count == 1 && combined.unicodeScalars.count == 2)
precondition(precomposed == combined)""",
            observe="Both spellings are one Character; the precomposed one is 2 UTF-8 bytes and 1 scalar, the combined one 3 bytes and 2 scalars, and they compare equal.",
            explain="count measures grapheme clusters, while utf8 and unicodeScalars measure the encoding. String equality uses canonical equivalence, so the two spellings are the same text.",
        ),
        2: dict(
            code=r"""let text = "\u{E9}😀"
precondition(text.count == 2)
precondition(text.utf8.count == 2 + 4)
precondition(text.utf16.count == 1 + 2)""",
            observe="Adding 😀 makes 2 Characters, 6 UTF-8 bytes and 3 UTF-16 code units.",
            explain="The emoji lies outside the Basic Multilingual Plane, so it takes 4 UTF-8 bytes and a UTF-16 surrogate pair while still being a single Character.",
        ),
        4: dict(
            code=r"""let text = "A😀B"
let byteOffset = Array(text.utf8).firstIndex(of: UInt8(ascii: "B"))!
precondition(byteOffset == 5)
let index = text.firstIndex(of: "B")!
precondition(text.distance(from: text.startIndex, to: index) == 2)
precondition(text[index] == "B")""",
            observe="B is at byte offset 5 but only 2 Characters from the start; the String.Index found in the same string reads B.",
            explain="A byte offset counts UTF-8 units, not Characters, and String has no Int subscript. Deriving the index from the string itself (firstIndex or index(after:)) is what keeps the emoji whole.",
        ),
        5: dict(
            code=r"""let empty = ""
precondition(empty.first == nil && empty.isEmpty)
let flag = "🇺🇸"
precondition(flag.count == 1 && flag.unicodeScalars.count == 2)
precondition(flag.first == "🇺🇸")
let family = "👨‍👩‍👧"
precondition(family.count == 1 && family.unicodeScalars.count == 5)""",
            observe="Empty text has no first Character; the flag is one Character of 2 scalars and the family emoji one Character of 5 scalars.",
            explain="Regional indicator pairs and zero-width-joiner sequences are single grapheme clusters, so first returns the whole cluster and empty text returns nil rather than an error.",
        ),
    },
    5: {
        1: dict(
            code=r"""let wrappedZero: Int? = 0
let absent: Int? = nil
precondition(wrappedZero != absent)
precondition(wrappedZero.map { $0 + 1 } == 1 && absent.map { $0 + 1 } == nil)
precondition((wrappedZero ?? 99) == 0 && (absent ?? 99) == 99)""",
            observe="Wrapped 0 maps to 1 and keeps 0 under ??, while nil stays nil under map and takes the default 99.",
            explain="Optional 0 is a present measurement that happens to be zero; nil is the absence of any measurement, so operations on the value run only for the wrapped case.",
        ),
        2: dict(
            code=r"""func display(_ reading: Int?) -> String { reading.map { "\($0)" } ?? "unknown" }
precondition(display(Int("42")) == "42")
precondition(display(Int("forty-two")) == "unknown")
precondition(display(0) == "0")""",
            observe="42 displays as 42, malformed text as unknown, and a real 0 still as 0.",
            explain="The label is chosen only at display time, so the stored value stays nil; Example B's -1 sentinel would have looked like a real reading.",
        ),
        4: dict(
            code=r"""let external = "forty-two"
let parsed = Int(external)
precondition(parsed == nil)
let outcome: String
if let value = parsed { outcome = "value:\(value)" } else { outcome = "rejected:\(external)" }
precondition(outcome == "rejected:forty-two")""",
            observe='Int("forty-two") is nil, and the optional binding routes it to rejected:forty-two.',
            explain="Writing Int(external)! would trap with Unexpectedly found nil while unwrapping, ending the program on ordinary bad input; binding the optional turns the failure into a reported outcome.",
        ),
        5: dict(
            code=r"""func parseCount(_ text: String?) -> Int? {
  guard let text, let value = Int(text), value >= 0 else { return nil }
  return value
}
precondition(parseCount("") == nil)
precondition(parseCount("0") == 0)
precondition(parseCount("-1") == nil)
precondition(parseCount("9223372036854775807") == Int.max)
precondition(parseCount("9223372036854775808") == nil)""",
            observe="Empty text and -1 are rejected, 0 and Int.max are accepted, and one past Int.max is rejected.",
            explain="Int(_:) itself returns nil for empty and out-of-range text, and the guard adds the nonnegative rule, so every boundary maps to nil or a value without a trap.",
        ),
    },
    6: {
        1: dict(
            code=r"""func classify(_ score: Int) -> String {
  switch score {
  case 0..<60: return "retry"
  case 60...100: return "pass"
  default: return "invalid"
  }
}
let predicted = ["retry", "pass", "invalid"]
precondition([59, 60, 101].map(classify) == predicted)""",
            observe="59 is retry, 60 is pass and 101 is invalid, matching the predictions written beforehand.",
            explain="0..<60 excludes 60, so 60 falls to the closed range 60...100; 101 lies outside both ranges and reaches default.",
        ),
        2: dict(
            code=r"""func classify(_ score: Int) -> String {
  switch score {
  case 0..<70: return "retry"
  case 70...100: return "pass"
  default: return "invalid"
  }
}
precondition(classify(69) == "retry" && classify(70) == "pass")
precondition(classify(60) == "retry" && classify(100) == "pass")""",
            observe="With the boundary at 70, 69 retries, 70 passes, and the old pass score 60 now retries.",
            explain="Both range bounds move together, and the adjacent tests move to 69 and 70 so they still sit on either side of the new boundary.",
        ),
        4: dict(
            code=r"""func overlapping(_ score: Int) -> String {
  switch score {
  case 0...60: return "retry"
  case 60...100: return "pass"
  default: return "invalid"
  }
}
func fixed(_ score: Int) -> String {
  switch score {
  case 0..<60: return "retry"
  case 60...100: return "pass"
  default: return "invalid"
  }
}
precondition(overlapping(60) == "retry" && fixed(60) == "pass")
precondition(overlapping(59) == fixed(59))""",
            observe="With 0...60 the score 60 is classified as retry; the exclusive 0..<60 gives pass, and 59 agrees in both.",
            explain="Swift takes the first matching case, so a closed range that includes 60 captures the boundary before the pass case is reached; only the boundary value exposes the defect.",
        ),
        5: dict(
            code=r"""func classify(_ score: Int) -> String {
  switch score {
  case 0..<60: return "retry"
  case 60...100: return "pass"
  default: return "invalid"
  }
}
precondition(classify(0) == "retry" && classify(100) == "pass")
precondition(classify(-1) == "invalid" && classify(101) == "invalid")""",
            observe="0 retries and 100 passes, while -1 and 101 are invalid.",
            explain="0 and 100 are the two ends of the valid domain and -1 and 101 the first values past them, so each range bound is tested from inside and outside.",
        ),
    },
    7: {
        1: dict(
            code=r"""let values = [2, 4, 6]
var total = 0
var trace: [Int] = []
for value in values {
  total += value
  trace.append(total)
}
precondition(trace == [2, 6, 12] && total == 12)""",
            observe="The accumulator is 2, then 6, then 12 after the three iterations.",
            explain="Each iteration adds one element to the running total, so after k iterations total equals the sum of the first k values; the recorded trace shows that invariant step by step.",
        ),
        2: dict(
            code=r"""let values = [2, -3, 4]
var total = 0
var kept: [Int] = []
for value in values where value >= 0 {
  total += value
  kept.append(value)
  precondition(total == kept.reduce(0, +))
}
precondition(total == 6 && kept == [2, 4])""",
            observe="-3 is skipped, so the total is 6 from the kept values 2 and 4.",
            explain="The invariant changes to: total equals the sum of the nonnegative values seen so far. The where clause skips negatives, and the in-loop precondition checks the invariant on every iteration.",
        ),
        4: dict(
            code=r"""let values = [3, 8, 8]
var index = 0
var steps = 0
while index < values.count && values[index] != 8 {
  index += 1
  steps += 1
}
precondition(index == 1 && steps == 1)""",
            observe="The loop stops at index 1 after one step.",
            explain="Without index += 1 the condition values[0] != 8 stays true forever. The progress variable must change in the body, and each step must move it toward the bound values.count.",
        ),
        5: dict(
            code=r"""func firstOffset(of target: Int, in values: [Int]) -> Int? {
  for (offset, value) in values.enumerated() where value == target {
    return offset
  }
  return nil
}
precondition(firstOffset(of: 4, in: []) == nil)
precondition(firstOffset(of: 4, in: [4]) == 0 && firstOffset(of: 9, in: [4]) == nil)
precondition(firstOffset(of: 4, in: [1, 4, 4, 4]) == 1)""",
            observe="The empty array gives nil, the singleton gives 0 or nil, and repeated matches report the first offset 1.",
            explain="The loop returns at the first match, so later duplicates are never visited; an empty input never enters the loop and falls through to nil.",
        ),
    },
    8: {
        1: dict(
            explain="In `area(width: Int, height: Int)` each parameter has one name, so `width` and `height` serve both as the argument labels at the call site and as the local names inside the body. In `increment(_ value: inout Int)` the underscore removes the label, so callers write `increment(&count)`, while the body still refers to the parameter as `value`. Labels describe the role of an argument to the caller; parameter names are what the implementation reads.",
        ),
        2: dict(
            code=r"""func volume(width: Int, height: Int, depth: Int) -> Int { width * height * depth }
precondition(volume(width: 2, height: 3, depth: 4) == 24)
precondition(volume(width: 2, height: 3, depth: 0) == 0)""",
            observe="A 2 by 3 by 4 box has volume 24, and depth 0 gives 0.",
            explain="The depth label makes the third dimension readable at the call site, so a caller cannot silently confuse it with width or height.",
        ),
        4: dict(
            explain="Calling `increment(count)` instead of `increment(&count)` is a compile error: swiftc reports that passing a value of type Int to an inout parameter requires an explicit &. The rule exists so that every call that may change the caller's storage is visible where it is written. Because compilation fails, no line of the program runs; adding the ampersand restores the call and Example B again observes 5.",
        ),
        5: dict(
            code=r"""func checkedArea(width: Int, height: Int) -> Int? {
  guard width >= 0, height >= 0 else { return nil }
  return width * height
}
precondition(checkedArea(width: 0, height: 4) == 0)
precondition(checkedArea(width: -3, height: 4) == nil)
precondition(checkedArea(width: -3, height: -4) == nil)""",
            observe="A zero width gives area 0, while one or two negative dimensions are rejected as nil.",
            explain="The policy accepts zero as a degenerate but valid shape and rejects negatives; checking each dimension matters because -3 times -4 would otherwise produce a plausible 12.",
        ),
    },
    9: {
        1: dict(
            code=r"""let original = [1, 2]
var changed = original
changed.append(3)
precondition(original == [1, 2] && original.count == 2)
precondition(changed == [1, 2, 3] && changed.count == 3)""",
            observe="original stays [1, 2] with count 2, while changed becomes [1, 2, 3] with count 3.",
            explain="Assigning an array copies the value; the shared buffer is duplicated only when changed is first mutated, so the append never reaches original.",
        ),
        2: dict(
            code=r"""let original = [1, 2, 3]
var copy = original
copy[0] = 10
precondition(copy == [10, 2, 3])
precondition(original == [1, 2, 3])""",
            observe="Replacing the first element of the copy gives [10, 2, 3] and original keeps [1, 2, 3].",
            explain="Subscript assignment is a mutation like append, so copy-on-write gives copy its own storage before element 0 changes.",
        ),
        4: dict(
            code=r"""var values: [Int] = []
values.reserveCapacity(20)
precondition(values.capacity >= 20 && values.isEmpty)
precondition(!values.indices.contains(0))
values.append(7)
precondition(values.indices.contains(0) && values[0] == 7)""",
            observe="After reserving 20 slots, index 0 is still not valid; it becomes valid only after appending 7.",
            explain="Valid indices come from count, not capacity, so values[0] on the reserved but empty array would trap with Index out of range. Checking indices.contains(0) shows the difference without crashing.",
        ),
        5: dict(
            code=r"""let values = [10, 20, 30, 40]
let empty = values[2..<2]
precondition(empty.isEmpty && empty.startIndex == 2)
let tail = values[1...]
precondition(tail.startIndex == 1 && tail.first == 20)
precondition(tail[tail.startIndex] == 20 && tail[1] == 20)""",
            observe="The empty slice 2..<2 starts at index 2, and the tail slice starts at index 1 where it reads 20.",
            explain="An ArraySlice shares its base array's indices, so tail[0] would trap; reading through startIndex or first works for any slice.",
        ),
    },
    10: {
        1: dict(
            code=r"""let counts = ["pear": 0]
let pear: Int? = counts["pear"]
let apple: Int? = counts["apple"]
precondition(pear == .some(0))
precondition(apple == .none)
precondition(counts["apple", default: 0] == 0)""",
            observe="Looking up pear gives .some(0), apple gives .none, and only the default subscript turns apple into 0.",
            explain="A lookup returns Int? because the key may be missing; the optional keeps a stored zero apart from absence until the caller deliberately supplies a default.",
        ),
        2: dict(
            code=r"""let tags = ["red", "blue", "red", "red"]
var counts: [String: Int] = [:]
for tag in tags { counts[tag, default: 0] += 1 }
precondition(counts == ["red": 3, "blue": 1])""",
            observe="Counting the four tags gives red: 3 and blue: 1.",
            explain="counts[tag, default: 0] reads 0 for a new tag and the += writes the incremented value back, inserting the key on its first occurrence.",
        ),
        4: dict(
            code=r"""struct Product: Hashable {
  let sku: String
}
let product = Product(sku: "A-17")
let storedKey = product.sku
precondition(Product(sku: storedKey) == product)
precondition(product.hashValue == Product(sku: "A-17").hashValue)""",
            observe="The stored SKU A-17 rebuilds an equal Product; hashValue matches only between values inside this same run.",
            explain="Swift seeds hashing randomly per process, so a hashValue written to disk will not match in the next run. Persist the stable field (the SKU) and let Hashable compute hashes in memory.",
        ),
        5: dict(
            code=r"""var stock = ["pear": 0]
precondition(stock["kiwi"] == nil && stock["pear"] == 0)
stock["pear"] = 5
precondition(stock.count == 1 && stock["pear"] == 5)
let merged = Dictionary([("fig", 1), ("fig", 2)], uniquingKeysWith: +)
precondition(merged == ["fig": 3])""",
            observe="kiwi is missing, pear is present at 0 and then replaced by 5 without a second entry, and duplicate fig pairs merge to 3.",
            explain="Assigning to an existing key replaces its value, and Dictionary(_:uniquingKeysWith:) makes the duplicate-key policy explicit instead of trapping.",
        ),
    },
    11: {
        1: dict(
            code=r"""let summary = (accepted: 3, rejected: 2)
precondition(summary.0 == summary.accepted && summary.1 == summary.rejected)
precondition(summary.accepted + summary.rejected == 5)""",
            observe="accepted is position 0 with 3 rows and rejected is position 1 with 2 rows; together they account for 5 rows.",
            explain="accepted counts rows that entered the result and rejected counts rows that did not, so their sum is every row read; the names make that meaning visible instead of relying on positions.",
        ),
        2: dict(
            code=r"""let summary = (accepted: 3, rejected: 2, skipped: 1)
let seen = summary.accepted + summary.rejected + summary.skipped
precondition(seen == 6)""",
            observe="With a skipped field of 1, the three fields account for 6 rows.",
            explain="skipped (for example blank lines) cannot be derived from the other two, so it earns a field; a total field would be redundant because it is always accepted + rejected + skipped.",
        ),
        4: dict(
            code=r"""struct LoosePage {
  var isLoading: Bool
  var count: Int?
  var error: String?
}
let contradictory = LoosePage(isLoading: true, count: 3, error: "offline")
precondition(contradictory.isLoading && contradictory.count != nil)
precondition(contradictory.error != nil)
enum PageState: Equatable {
  case loading
  case ready(Int)
  case failed(String)
}
precondition(PageState.ready(3) != .failed("offline"))""",
            observe="The struct accepts loading, a count and an error at once, while each PageState value is exactly one of loading, ready or failed.",
            explain="Three independent fields allow eight combinations, most of them meaningless; the enum's cases admit only the three real states, so the contradiction cannot be built.",
        ),
        5: dict(
            code=r"""enum Load {
  case loading
  case ready(Int)
  case failed(String)
  case cancelled
}
func label(_ state: Load) -> String {
  switch state {
  case .loading: return "loading"
  case .ready(let count): return "ready:\(count)"
  case .failed(let reason): return "failed:\(reason)"
  case .cancelled: return "cancelled"
  }
}
precondition(label(.cancelled) == "cancelled" && label(.ready(2)) == "ready:2")""",
            observe="After adding cancelled and handling it, label returns cancelled for the new case and ready:2 as before.",
            explain="Before the new case clause was written, swiftc stopped with switch must be exhaustive at this switch; that error list is the set of consumers to update, which a default clause would have hidden.",
        ),
    },
    12: {
        1: dict(
            code=r"""var first = Inventory(stock: 5)
var second = first
precondition(first.stock == 5 && second.stock == 5)
precondition(second.reserve(2))
precondition(first.stock == 5 && second.stock == 3)
precondition(first.reserve(0) && first.stock == 5)""",
            observe="Both copies start at 5; reserving 2 from second leaves first at 5 and second at 3, and reserving 0 from first keeps 5.",
            explain="Inventory is a struct, so var second = first copies the stock, and each mutating reserve changes only the copy it is called on.",
        ),
        2: dict(
            helpers=r"""extension Inventory {
  mutating func restock(_ amount: Int) -> Bool {
    guard amount > 0 else { return false }
    let result = stock.addingReportingOverflow(amount)
    guard !result.overflow else { return false }
    stock = result.partialValue
    return true
  }
}""",
            code=r"""var inventory = Inventory(stock: 3)
precondition(inventory.restock(4) && inventory.stock == 7)
precondition(!inventory.restock(0) && !inventory.restock(-2))
precondition(!inventory.restock(Int.max) && inventory.stock == 7)""",
            observe="Restocking 4 raises 3 to 7; 0, -2 and an overflowing Int.max are refused and the stock stays 7.",
            explain="The extension lives in the same file, so it may use the private setter, and it validates before writing, so a refused restock never changes stock.",
        ),
        4: dict(
            code=r"""struct Careless {
  var stock: Int
  mutating func reserve(_ amount: Int) -> Bool {
    stock -= amount
    return stock >= 0
  }
}
var careless = Careless(stock: 3)
precondition(!careless.reserve(4) && careless.stock == -1)
var inventory = Inventory(stock: 3)
precondition(!inventory.reserve(4) && inventory.stock == 3)""",
            observe="Subtracting first reports failure but leaves stock at -1; Inventory refuses the same request and keeps 3.",
            explain="The careless version mutates before validating, so a rejected request still corrupts state; the guard in Inventory.reserve checks the amount first and changes stock only on success.",
        ),
        5: dict(
            code=r"""var inventory = Inventory(stock: 3)
precondition(inventory.reserve(0) && inventory.stock == 3)
precondition(!inventory.reserve(4) && inventory.stock == 3)
precondition(inventory.reserve(3) && inventory.stock == 0)""",
            observe="Reserving 0 succeeds without change, 4 is refused, and exactly 3 succeeds and leaves 0.",
            explain="amount <= stock admits the exact-stock case, and amount >= 0 admits zero, so the only refusal is the request that exceeds the stock.",
        ),
    },
    13: {
        1: dict(
            code=r"""let first = Counter()
let second = first
precondition(first === second)
second.increment()
precondition(first.value == 1)
precondition(ObjectIdentifier(first) == ObjectIdentifier(second))""",
            observe="Before and after the increment, first and second refer to one object, so first reads 1.",
            explain="Assigning a class instance copies the reference, not the object; the drawing has two names pointing at one Counter box, and ObjectIdentifier confirms the single identity.",
        ),
        2: dict(
            code=r"""let first = Counter()
let second = Counter()
second.increment()
precondition(first.value == 0 && second.value == 1)
precondition(first !== second)""",
            observe="Incrementing the separately created second leaves first at 0 and second at 1.",
            explain="Each Counter() call allocates its own object, so mutation through one reference cannot be seen through the other.",
        ),
        4: dict(
            code=r"""let live = Counter()
let alias = live
let snapshot = live.value
live.increment()
precondition(alias.value == 1)
precondition(snapshot == 0)""",
            observe="The alias sees 1 after the increment, while the Int snapshot taken earlier stays 0.",
            explain="let alias = live copies only the reference, so it is not a snapshot; copying the Int value out is what preserves the earlier state.",
        ),
        5: dict(
            code=r"""let first = Counter()
let second = Counter()
first.increment()
second.increment()
precondition(first.value == second.value && first !== second)
first.increment()
precondition(first.value == 2 && second.value == 1)""",
            observe="Both objects read 1 yet are distinct; a further increment on first gives 2 and 1.",
            explain="Equal property values say nothing about identity; === compares identity, and the later divergence shows the objects were never shared.",
        ),
    },
    14: {
        1: dict(
            code=r"""let rectangleFields = Mirror(reflecting: Rectangle(width: 3, height: 4)).children
precondition(rectangleFields.map(\.label) == ["width", "height"])
let temperatureFields = Mirror(reflecting: Temperature(celsius: 0)).children
precondition(temperatureFields.map(\.label) == ["celsius"])""",
            observe="Rectangle stores only width and height, and Temperature stores only celsius.",
            explain="Mirror lists stored properties; area and fahrenheit are absent because they are computed from the stored values every time they are read.",
        ),
        2: dict(
            helpers=r"""extension Rectangle {
  var perimeter: Int { 2 * (width + height) }
}""",
            code=r"""var rectangle = Rectangle(width: 3, height: 4)
precondition(rectangle.perimeter == 14)
rectangle.width = 5
precondition(rectangle.perimeter == 18)""",
            observe="The perimeter is 14 for 3 by 4 and 18 after the width becomes 5.",
            explain="A computed property added in an extension needs no storage, so it follows width without any update code.",
        ),
        4: dict(
            code=r"""struct StaleRectangle {
  var width: Int
  var height: Int
  var area: Int
}
var stale = StaleRectangle(width: 3, height: 4, area: 12)
stale.width = 5
precondition(stale.area == 12)
var derived = Rectangle(width: 3, height: 4)
derived.width = 5
precondition(derived.area == 20)""",
            observe="After widening to 5 the stored area still says 12, while the computed area says 20.",
            explain="A stored copy of derived data must be updated by every writer; nothing updates stale.area, so it goes out of date. Computing area removes that obligation.",
        ),
        5: dict(
            code=r"""precondition(Rectangle(width: 0, height: 4).area == 0)
var temperature = Temperature(celsius: 0)
precondition(temperature.fahrenheit == 32)
temperature.celsius = 37.5
precondition(abs(temperature.fahrenheit - 99.5) < 1e-9)
temperature.fahrenheit = 98.6
precondition(abs(temperature.celsius - 37) < 1e-9)""",
            observe="A zero width gives area 0; 0 C is 32 F, 37.5 C is 99.5 F, and setting 98.6 F stores 37 C.",
            explain="37.5 * 9 / 5 + 32 is 99.5, and (98.6 - 32) * 5 / 9 is 37; 98.6 is not exact in binary, so the tolerance compares the conversion rather than exact bits.",
        ),
    },
    15: {
        1: dict(
            code=r"""let values = [1, 2, 3]
let doubled = values.map { $0 * 2 }
precondition(doubled == [2, 4, 6])
precondition(values == [1, 2, 3] && doubled.count == values.count)""",
            observe="map gives [2, 4, 6], and values remains [1, 2, 3] with the same count.",
            explain="map calls the closure once per element and builds a new array of the same length; it never writes to its source.",
        ),
        2: dict(
            code=r"""let values = [1, 2, 3, 4]
let evensDoubled = values.filter { $0 % 2 == 0 }.map { $0 * 2 }
precondition(evensDoubled == [4, 8])""",
            observe="Filtering keeps 2 and 4, and mapping doubles them to [4, 8].",
            explain="Filtering first means the map closure only sees even values; mapping first and filtering afterward would test the doubled values, which are all even.",
        ),
        4: dict(
            code=r"""var factor = 2
let live = { (value: Int) in value * factor }
let frozen = { [factor] (value: Int) in value * factor }
factor = 5
precondition(live(3) == 15)
precondition(frozen(3) == 6)""",
            observe="After factor becomes 5, the live closure returns 15 while the capture-list closure still returns 6.",
            explain="A closure captures the variable itself, so it reads the value current at call time; [factor] copies the value when the closure is created.",
        ),
        5: dict(
            code=r"""precondition([Int]().map { $0 * 2 }.isEmpty)
let parsed = ["1", "x", "3"].map { Int($0) }
precondition(parsed == [1, nil, 3])
let valid = ["1", "x", "3"].compactMap { Int($0) }
precondition(valid == [1, 3])""",
            observe="Mapping an empty array gives an empty array; map keeps nil for x, while compactMap drops it and returns [1, 3].",
            explain="When the closure returns Int?, map produces [Int?] and preserves the failure in position; compactMap discards failures, which is a policy choice, not a neutral default.",
        ),
    },
    16: {
        1: dict(
            code=r"""let lines = ["pear,2", "bad", ",3", "pear,x", "pear,-1", "apple,3"]
let verdicts = lines.map { importRows([$0]).rejected == 0 ? "ok" : "rejected" }
precondition(verdicts == ["ok", "rejected", "rejected", "rejected", "rejected", "ok"])""",
            observe="pear,2 and apple,3 pass; bad, ,3, pear,x and pear,-1 are rejected.",
            explain="bad fails the two-field check, ,3 has an empty name, x fails Int parsing, and -1 fails the nonnegative check; each line stops at its first failed guard condition.",
        ),
        2: dict(
            code=r"""let result = importRows(["pear,2", "apple,3", "pear,4", "apple,1"])
precondition(result.counts == ["pear": 6, "apple": 4])
precondition(result.rejected == 0)""",
            observe="Adding apple,1 raises apple to 4 while pear stays 6, with nothing rejected.",
            explain="counts[name, default: 0] += quantity adds to an existing key instead of replacing it, so a duplicate name accumulates.",
        ),
        4: dict(
            code=r"""func lenientQuantity(_ text: Substring) -> Int { Int(text) ?? 0 }
precondition(lenientQuantity("no") == lenientQuantity("0"))
let result = importRows(["pear,0", "pear,no"])
precondition(result.counts == ["pear": 0] && result.rejected == 1)""",
            observe="The lenient parser makes no and 0 indistinguishable; the importer keeps pear at 0 and counts one rejection.",
            explain="Int(text) ?? 0 turns malformed input into a valid-looking zero, hiding the defect; the importer's guard rejects the line so it is reported instead.",
        ),
        5: dict(
            code=r"""precondition(importRows([",2"]).rejected == 1)
precondition(importRows(["pear,2,extra"]).rejected == 1)
precondition(importRows(["pear,0"]).counts == ["pear": 0])
let empty = importRows([])
precondition(empty.counts.isEmpty && empty.rejected == 0)""",
            observe="An empty name and an extra field are each rejected, pear,0 is accepted as 0, and no input gives no counts and no rejections.",
            explain="omittingEmptySubsequences: false keeps the empty name and the extra field visible to the field-count and name checks, and an empty list simply never enters the loop.",
        ),
    },
    17: {
        1: dict(
            code=r"""let prices: [any Pricer] = [FlatPrice(unit: 3), CappedPrice(unit: 3, cap: 10)]
precondition(type(of: prices[0]) == FlatPrice.self)
precondition(type(of: prices[1]) == CappedPrice.self)
precondition(prices[0].cost(units: 4) == 3 * 4)
precondition(prices[1].cost(units: 4) == min(3 * 4, 10))""",
            observe="The first element is a FlatPrice that returns 12, and the second is a CappedPrice that returns min(12, 10) = 10.",
            explain="The call cost(units:) is written once against any Pricer; at run time it dispatches to the conforming type stored in each box, so the same line reaches FlatPrice.cost and then CappedPrice.cost.",
        ),
        2: dict(
            code=r"""func totals(_ prices: [any Pricer], units: Int) -> [Int] {
  prices.map { $0.cost(units: units) }
}
let prices: [any Pricer] = [FlatPrice(unit: 3), CappedPrice(unit: 3, cap: 10), FlatPrice(unit: 5)]
precondition(totals(prices, units: 4) == [12, 10, 20])""",
            observe="Adding FlatPrice(unit: 5) yields a third total of 20 while the first two stay 12 and 10.",
            explain="totals depends only on the Pricer requirement, so a new conforming value is accepted without editing the consumer.",
        ),
        4: dict(
            code=r"""struct DollarPrice: Pricer {
  let dollars: Int
  func cost(units: Int) -> Int { dollars * units }
}
let cents: any Pricer = FlatPrice(unit: 300)
let dollars: any Pricer = DollarPrice(dollars: 3)
precondition(cents.cost(units: 2) == 600 && dollars.cost(units: 2) == 6)
let fixed: any Pricer = FlatPrice(unit: 3 * 100)
precondition(fixed.cost(units: 2) == cents.cost(units: 2))""",
            observe="For the same price, one conformer returns 600 (cents) and the other 6 (dollars); converting before conforming makes them agree.",
            explain="Both types satisfy the signature, so the compiler accepts them, but the protocol never stated the unit. The fix is a documented contract (cost is in cents) that every conformer honors.",
        ),
        5: dict(
            code=r"""let capped = CappedPrice(unit: 3, cap: 12)
precondition(capped.cost(units: 0) == 0)
precondition(capped.cost(units: 4) == 12)
precondition(capped.cost(units: 5) == 12)
precondition(FlatPrice(unit: 3).cost(units: 0) == 0)""",
            observe="Zero units cost 0 for both policies, 4 units hit the cap of 12 exactly, and 5 units stay capped at 12.",
            explain="min(unit * units, cap) returns the product at the boundary where the two are equal, so the exact-cap case and the zero case both behave like the flat price.",
        ),
    },
    18: {
        1: dict(
            code=r"""let number = larger(3, 8)
let word = larger("apple", "pear")
let pair = Pair(first: "left", second: "right")
precondition(type(of: number) == Int.self)
precondition(type(of: word) == String.self)
precondition(type(of: pair) == Pair<String>.self)""",
            observe="T is inferred as Int for larger(3, 8), String for the words, and the pair is a Pair<String>.",
            explain="The compiler infers T from the arguments at each call, so no annotation is needed and the result keeps that concrete type.",
        ),
        2: dict(
            code=r"""precondition(larger(2.5, 1.5) == 2.5)
let tie = larger(2.0, 2.0)
precondition(tie == 2.0 && type(of: tie) == Double.self)""",
            observe="larger picks 2.5 from the Double pair, and the tie 2.0, 2.0 returns 2.0 as a Double.",
            explain="Double conforms to Comparable, so the same generic body is reused with T = Double; a numeric tie returns an equal value either way.",
        ),
        4: dict(
            code=r"""func describe<T: CustomStringConvertible>(_ value: T) -> String {
  "value: \(value.description)"
}
precondition(describe(7) == "value: 7")
precondition(describe("pear") == "value: pear")""",
            observe="Constraining T to CustomStringConvertible lets describe produce value: 7 and value: pear.",
            explain="Without the constraint, swiftc rejects value.description with value of type 'T' has no member 'description', because an unconstrained T promises no members. The constraint states the capability the body uses.",
        ),
        5: dict(
            code=r"""struct Ranked: Comparable {
  let rank: Int
  let tag: String
  static func < (left: Ranked, right: Ranked) -> Bool { left.rank < right.rank }
  static func == (left: Ranked, right: Ranked) -> Bool { left.rank == right.rank }
}
let winner = larger(Ranked(rank: 1, tag: "left"), Ranked(rank: 1, tag: "right"))
precondition(winner.tag == "left")""",
            observe="With equal ranks, larger returns the value tagged left.",
            explain="left >= right is true on a tie, so larger documents and returns its first argument; the tag reveals that choice when equal values are distinguishable.",
        ),
    },
    19: {
        1: dict(
            code=r"""let produced = read(IntegerSource())
precondition(type(of: produced) == Int.self)
let doubled = produced * 2
precondition(doubled == 14)""",
            observe="read returns an Int, so it can be multiplied directly to give 14.",
            explain="IntegerSource.produce returns Int, which fixes Item = Int; read returns P.Item, so the caller receives Int without any cast.",
        ),
        2: dict(
            code=r"""struct NameSource: Producer {
  func produce() -> String { "pear" }
}
let name = read(NameSource())
precondition(name.uppercased() == "PEAR")
precondition(read(IntegerSource()) == 7)""",
            observe="read on NameSource returns the String pear, while IntegerSource still returns 7.",
            explain="Each conformance chooses its own Item from the produce return type, and the same generic read preserves whichever type that is.",
        ),
        4: dict(
            explain="A function declared -> some Sequence<String> promises one hidden concrete type for every call. Returning an array on one branch and a Set on another makes swiftc report that the return statements do not have matching underlying types. Either convert every branch to the same type (for example Array), or return an existential any Sequence<String> when the caller truly does not need a fixed type.",
        ),
        5: dict(
            helpers=r"""func makeNoLabels() -> some Sequence<String> { [String]() }""",
            code=r"""precondition(Array(makeNoLabels()).isEmpty)
var count = 0
for _ in makeLabels() { count += 1 }
precondition(count == 2)""",
            observe="The empty opaque sequence produces no elements, and iterating makeLabels counts 2.",
            explain="Callers use only Sequence behavior, so an empty array and a two-element array both work behind some Sequence<String> without exposing their type.",
        ),
    },
    20: {
        1: dict(
            code=r"""let values = [10, 20, 30, 40]
let slice = values[1...2]
precondition(slice.count == 2)
precondition(slice.startIndex == 1 && slice.endIndex == 3)""",
            observe="The slice has count 2 but startIndex 1 and endIndex 3.",
            explain="count measures how many elements the slice holds, while startIndex is inherited from the base array, so the two answer different questions.",
        ),
        2: dict(
            code=r"""let values = [10, 20, 30, 40]
let slice = values[1...2]
var seen: [Int] = []
for index in slice.indices { seen.append(slice[index]) }
precondition(seen == [20, 30])
precondition(Array(slice.indices) == [1, 2])""",
            observe="Walking slice.indices visits indices 1 and 2 and reads 20 and 30.",
            explain="slice.indices yields the slice's real positions, so every subscript is valid regardless of where the slice starts.",
        ),
        4: dict(
            code=r"""let values = [10, 20, 30, 40]
let slice = values[1...2]
precondition(!slice.indices.contains(0))
var total = 0
for offset in 0..<slice.count {
  total += slice[slice.index(slice.startIndex, offsetBy: offset)]
}
precondition(total == 50)""",
            observe="Index 0 is not in the slice, and offsetting from startIndex sums 20 + 30 = 50.",
            explain="Looping slice[0..<count] would read index 0, which traps because the slice starts at 1; offsets must be converted to indices from startIndex.",
        ),
        5: dict(
            code=r"""let empty = [1, 2, 3][3..<3]
precondition(empty.isEmpty && empty.startIndex == 3)
final class OneShot: Sequence, IteratorProtocol {
  var remaining: [Int]
  init(_ values: [Int]) { remaining = values }
  func next() -> Int? { remaining.isEmpty ? nil : remaining.removeFirst() }
}
let stream = OneShot([1, 2])
precondition(Array(stream) == [1, 2])
precondition(Array(stream).isEmpty)""",
            observe="The empty slice starts at 3 with no elements; the one-shot stream yields [1, 2] once and then nothing.",
            explain="OneShot is its own iterator and consumes its state, so a second traversal sees an empty sequence; Sequence does not promise repeatable iteration.",
        ),
    },
    21: {
        1: dict(
            code=r"""func trace(_ text: String) -> String {
  do {
    let value = try parseQuantity(text)
    return "returned \(value)"
  } catch {
    return "threw"
  }
}
precondition(trace("3") == "returned 3")
precondition(trace("-1") == "threw" && trace("x") == "threw")""",
            observe="3 follows the normal path and returns 3, while -1 and x leave through the throw.",
            explain="parseQuantity either reaches return value or exits at throw; the guard decides which, and control resumes in the caller's catch only on the throwing path.",
        ),
        2: dict(
            code=r"""enum QuantityProblem: Error, Equatable {
  case malformed
  case negative
}
func strictQuantity(_ text: String) throws(QuantityProblem) -> Int {
  guard let value = Int(text) else { throw .malformed }
  guard value >= 0 else { throw .negative }
  return value
}
func problem(_ text: String) -> QuantityProblem? {
  do { _ = try strictQuantity(text) } catch { return error }
  return nil
}
precondition(problem("x") == .malformed && problem("-1") == .negative)
precondition(problem("4") == nil)""",
            observe="x reports malformed, -1 reports negative, and 4 reports no problem.",
            explain="Splitting the guard into two conditions with distinct cases lets the caller tell a typing mistake from a domain violation; the typed throws makes the caught error a QuantityProblem.",
        ),
        4: dict(
            code=r"""precondition((try? parseQuantity("x")) == nil)
precondition((try? parseQuantity("-1")) == nil)
let kept = Result { try parseQuantity("-1") }
if case .failure(let error) = kept { precondition(error is QuantityError) }""",
            observe="try? turns both malformed and negative input into the same nil, while Result keeps the QuantityError.",
            explain="When the reason must be reported, try? discards the evidence; do/catch or Result preserves the error for the caller to inspect.",
        ),
        5: dict(
            code=r"""func accepts(_ text: String) -> Bool { (try? parseQuantity(text)) != nil }
precondition(!accepts(""))
let zero = try parseQuantity("0")
precondition(zero == 0)
precondition(!accepts("99999999999999999999"))""",
            observe="Empty text is rejected, 0 is accepted as 0, and a value beyond Int.max is rejected.",
            explain='Int("") and Int on an overflowing literal both return nil, so the guard throws; 0 passes the value >= 0 check exactly.',
        ),
    },
    22: {
        1: dict(
            code=r"""var parent: Parent? = Parent()
var child: Child? = Child()
parent?.child = child
child?.parent = parent
weak var childObserver = child
child = nil
precondition(childObserver != nil)
parent = nil
precondition(childObserver == nil)""",
            observe="The child survives losing its local variable while the parent still holds it, and disappears once the parent is gone.",
            explain="The arrow from Parent.child is strong, so it keeps the child alive; the arrow from Child.parent is weak, so nothing keeps the parent alive after parent = nil, and the child follows.",
        ),
        2: dict(
            code=r"""var owner: Owner? = Owner()
var second: Owner? = owner
weak var observer = owner
owner = nil
precondition(observer != nil && second != nil)
second = nil
precondition(observer == nil)""",
            observe="The observer survives clearing owner because second still holds the object, and clears when second is set to nil.",
            explain="A weak reference becomes nil only after the last strong reference goes away, so the second owner delays deallocation until it is released.",
        ),
        4: dict(
            code=r"""final class Ticker {
  var count = 0
  var onTick: (() -> Void)?
  func startStrong() { onTick = { self.count += 1 } }
  func startWeak() { onTick = { [weak self] in self?.count += 1 } }
}
var leaky: Ticker? = Ticker()
leaky?.startStrong()
weak var leakObserver = leaky
leaky = nil
precondition(leakObserver != nil)
leakObserver?.onTick = nil
precondition(leakObserver == nil)
var fixed: Ticker? = Ticker()
fixed?.startWeak()
weak var fixedObserver = fixed
fixed = nil
precondition(fixedObserver == nil)""",
            observe="The strongly capturing ticker outlives its variable until onTick is cleared; the weakly capturing ticker is freed immediately.",
            explain="The object owns the closure and the closure owns self, forming a cycle ARC cannot break; [weak self] removes the closure's strong arrow.",
        ),
        5: dict(
            code=r"""final class Screen {
  var shown: [String] = []
}
var screen: Screen? = Screen()
let show = { [weak screen] (text: String) -> Bool in
  guard let screen else { return false }
  screen.shown.append(text)
  return true
}
precondition(show("first") && screen?.shown == ["first"])
screen = nil
precondition(!show("late"))""",
            observe="The callback delivers first while the screen exists and returns false for late after it is gone.",
            explain="The capture list holds the screen weakly, so a late callback finds nil and reports that nothing was delivered instead of reviving or crashing.",
        ),
    },
    23: {
        1: dict(
            code=r"""let invalid = Item(name: "", quantity: -1)
let data = try JSONEncoder().encode(invalid)
let restored = try JSONDecoder().decode(Item.self, from: data)
precondition(restored == invalid && !restored.isValid)""",
            observe="Even an invalid item with an empty name and -1 round-trips to an equal value.",
            explain="The round-trip proves the encoder and decoder agree on the field mapping; it says nothing about whether the values satisfy business rules.",
        ),
        2: dict(
            code=r"""struct Described: Codable, Equatable {
  let name: String
  let description: String?
}
let missing = try JSONDecoder().decode(
  Described.self, from: Data(#"{"name":"pear"}"#.utf8))
precondition(missing.description == nil)
let present = try JSONDecoder().decode(
  Described.self, from: Data(#"{"name":"pear","description":"ripe"}"#.utf8))
precondition(present.description == "ripe")""",
            observe="Without the key, description decodes as nil; with it, description is ripe.",
            explain="Synthesized Codable uses decodeIfPresent for Optional properties, so an absent key is accepted as nil while a present one is decoded normally.",
        ),
        4: dict(
            code=r"""let data = Data(#"{"name":"","quantity":-5}"#.utf8)
let decoded = try JSONDecoder().decode(Item.self, from: data)
precondition(decoded.name.isEmpty && decoded.quantity == -5)
precondition(!decoded.isValid)""",
            observe="The decoder accepts an empty name and quantity -5 without complaint, and only isValid reports the violation.",
            explain="Synthesized Codable checks JSON shape and types, not business rules, so a validation step must run before the item is trusted.",
        ),
        5: dict(
            code=r"""func decodes(_ json: String) -> Bool {
  (try? JSONDecoder().decode(Item.self, from: Data(json.utf8))) != nil
}
precondition(!decodes(#"{"name":"pear","#))
precondition(!decodes(#"{"name":"pear"}"#))
precondition(decodes(#"{"name":"pear","quantity":1,"color":"green"}"#))""",
            observe="Truncated JSON and a missing quantity fail to decode, while an unknown color field is ignored.",
            explain="Malformed syntax raises a data-corrupted error and a missing required key raises keyNotFound, but synthesized decoding silently skips keys it does not model.",
        ),
    },
    24: {
        1: dict(
            code=r"""let manager = FileManager.default
func useOwnedDirectory() throws -> URL {
  let root = manager.temporaryDirectory.appendingPathComponent(
    UUID().uuidString, isDirectory: true)
  try manager.createDirectory(at: root, withIntermediateDirectories: true)
  defer { try? manager.removeItem(at: root) }
  let file = root.appendingPathComponent("trace.txt")
  try Data("used".utf8).write(to: file)
  precondition(manager.fileExists(atPath: file.path))
  return root
}
let root = try useOwnedDirectory()
precondition(!manager.fileExists(atPath: root.path))""",
            observe="The file exists while the function runs, and the directory is gone once the function returns.",
            explain="Acquisition creates a fresh directory, use writes inside it, and defer runs the cleanup on the way out of the scope, whether by return or by throw.",
        ),
        2: dict(
            code=r"""let manager = FileManager.default
let root = manager.temporaryDirectory.appendingPathComponent(
  UUID().uuidString, isDirectory: true)
try manager.createDirectory(at: root, withIntermediateDirectories: true)
defer { try? manager.removeItem(at: root) }
let first = root.appendingPathComponent("a.txt")
let second = root.appendingPathComponent("b.txt")
try Data("alpha".utf8).write(to: first)
try Data("beta".utf8).write(to: second)
let firstText = try String(contentsOf: first, encoding: .utf8)
let secondText = try String(contentsOf: second, encoding: .utf8)
precondition(firstText == "alpha" && secondText == "beta")""",
            observe="a.txt reads back alpha and b.txt reads back beta under the same owned directory.",
            explain="Each file gets its own name inside the directory this code created, and the single defer removes both when the scope ends.",
        ),
        4: dict(
            explain="The worker writes into its container's temporary directory, and that filesystem is discarded when the container is replaced, so a file written in one run is not there for the next. Temporary storage is for scratch data within one run; anything that must persist needs a mounted volume or an external store, and the reader must handle the file being absent.",
        ),
        5: dict(
            code=r"""let manager = FileManager.default
let root = manager.temporaryDirectory.appendingPathComponent(
  UUID().uuidString, isDirectory: true)
try manager.createDirectory(at: root, withIntermediateDirectories: true)
defer { try? manager.removeItem(at: root) }
let blank = root.appendingPathComponent("blank.bin")
try Data().write(to: blank)
let blankBytes = try Data(contentsOf: blank)
precondition(blankBytes.isEmpty)
var missingFailed = false
do { _ = try Data(contentsOf: root.appendingPathComponent("absent.bin")) } catch {
  missingFailed = true
}
precondition(missingFailed)""",
            observe="The empty file reads back as zero bytes, while reading a missing file throws.",
            explain="An empty file exists and has no content; a missing file is a different outcome that raises an error, so the reader can tell no data from no file.",
        ),
    },
    25: {
        1: dict(
            code=r"""let seconds: TimeInterval = 5400
let minutes = seconds / 60
precondition(minutes == 90)
precondition(minutes * 60 == seconds)
let duration = Duration.seconds(5400)
precondition(duration.components.seconds / 60 == 90)""",
            observe="5,400 seconds is 90 minutes, and 90 minutes converts back to exactly 5,400 seconds.",
            explain="An elapsed duration is a count of seconds with no calendar involved, so dividing and multiplying by 60 converts losslessly in both directions.",
        ),
        2: dict(
            code=r"""var calendar = Calendar(identifier: .gregorian)
calendar.timeZone = TimeZone(identifier: "America/New_York")!
let start = ISO8601DateFormatter().date(from: "2025-03-08T12:00:00-05:00")!
let plusSeconds = start.addingTimeInterval(86_400)
let nextLocalDay = calendar.date(byAdding: .day, value: 1, to: start)!
precondition(calendar.component(.hour, from: plusSeconds) == 13)
precondition(calendar.component(.hour, from: nextLocalDay) == 12)
precondition(nextLocalDay.timeIntervalSince(start) == 82_800)""",
            observe="Across the March 9 daylight-saving change in New York, adding 86,400 seconds lands at 13:00 local, while the calendar's next day is 12:00 and only 82,800 seconds later.",
            explain="A fixed 86,400 seconds is an elapsed duration; next local day is a calendar question that depends on the time zone, and a 23-hour day breaks the equivalence.",
        ),
        4: dict(
            code=r"""let fixedOffset = TimeZone(secondsFromGMT: -5 * 3600)!
let newYork = TimeZone(identifier: "America/New_York")!
let parser = ISO8601DateFormatter()
let winter = parser.date(from: "2025-01-15T12:00:00Z")!
let summer = parser.date(from: "2025-07-15T12:00:00Z")!
precondition(fixedOffset.secondsFromGMT(for: winter) == newYork.secondsFromGMT(for: winter))
precondition(fixedOffset.secondsFromGMT(for: summer) == -18_000)
precondition(newYork.secondsFromGMT(for: summer) == -14_400)""",
            observe="In January the -05:00 offset and New York agree, but in July New York is -04:00 while the fixed offset stays -05:00.",
            explain="An offset describes one instant; a time-zone identifier carries the rules that change the offset over the year, so storing -05:00 as the user's zone breaks future summer times.",
        ),
        5: dict(
            code=r"""let parser = ISO8601DateFormatter()
let late = parser.date(from: "2025-01-01T23:50:00Z")!
let early = parser.date(from: "2025-01-02T00:10:00Z")!
precondition(early.timeIntervalSince(late) == 1200)
precondition(parser.date(from: "not a date") == nil)
precondition(parser.date(from: "2025-01-01T10:00:00") == nil)""",
            observe="23:50 to 00:10 the next day is 1,200 seconds, while garbage text and a timestamp without an offset both parse to nil.",
            explain="Instants subtract without regard to the date change at midnight, and the internet date-time format requires an offset, so incomplete text is refused instead of being guessed.",
        ),
    },
    26: {
        1: dict(
            code=r"""func total(_ values: [Int]) -> Int { values.reduce(0, +) }
func render(_ total: Int) -> String { "total=\(total)" }
let sum = total([4, 6])
precondition(sum == 10)
precondition(render(sum) == "total=10")""",
            observe="The core returns the number 10, and presentation separately turns it into total=10.",
            explain="total is the reusable calculation with no knowledge of text, while render only formats; that split is the library-versus-executable boundary a package makes explicit.",
        ),
        2: dict(
            explain="Copy fixtures/JourneyCore into your own workspace and run swift build in the copied directory. It compiles the JourneyCore library and the journey-demo executable and ends with Build complete!; in the reference run on swift:6.3.3-noble the last steps were Linking journey-demo and Build complete! (3.01s). No dependency is fetched, because the manifest declares none.",
        ),
        3: dict(
            explain="In the copied package run swift test, then swift run journey-demo. The reference run on swift:6.3.3-noble reported Executed 4 tests, with 0 failures and printed JourneyCore: 1/2 complete; round trip passed. The tests exercise the library through @testable import, and the executable consumes only its public API.",
        ),
        4: dict(
            explain="Removing public from StudyPlan.completedCount still compiles inside JourneyCore, but the JourneyDemo target then fails with 'completedCount' is inaccessible due to 'internal' protection level, as the reference build showed. Symbols default to internal, visible only within their module; anything another target must call needs public, which also makes it a compatibility promise.",
        ),
        5: dict(
            explain="Inside the copied package run swift package clean, then swift build. Clean removes build products under that package's .build directory and leaves sources alone; the rebuild recreates .build in the same place, which the reference run confirmed was the only output location. Never point cleanup at a directory you did not create.",
        ),
    },
    27: {
        1: dict(
            code=r"""let cases = [(-2, 0), (0, 0), (3, 3)]
func passes(_ candidate: (Int) -> Int) -> Bool {
  cases.allSatisfy { candidate($0.0) == $0.1 }
}
precondition(passes { max(0, $0) })
precondition(!passes { $0 })
precondition(!passes { abs($0) })
precondition(!passes { _ in 0 })""",
            observe="The real clamp passes, identity and abs fail on -2, and always-zero fails on 3.",
            explain="Each fixture earns its place by rejecting some wrong implementation: the negative row catches missing clamping or sign flipping, and the positive row catches a constant result.",
        ),
        2: dict(
            code=r"""precondition(max(0, Int.min) == 0)
precondition(Int.min.magnitude == UInt(Int.max) + 1)
precondition(Int.min.addingReportingOverflow(-1).overflow)""",
            observe="Clamping Int.min gives 0, and its magnitude is one more than Int.max.",
            explain="max(0, Int.min) never negates, so it is safe; -Int.min or abs(Int.min) would trap because the positive value does not fit in Int.",
        ),
        3: dict(
            explain='Add this method to PlanTests: func testBlankTitleIsRejected() throws { XCTAssertThrowsError(try StudyItem(id: "two", title: "   ")) { error in XCTAssertEqual(error as? PlanError, .invalidItem) } }. In the reference copy, swift test then reported Executed 5 tests, with 0 failures. The test fails if the initializer stops trimming whitespace or reports a different error.',
        ),
        4: dict(
            code=r"""func wrongClamp(_ value: Int) -> Int { value <= 0 ? 1 : value }
precondition(wrongClamp(0) == wrongClamp(0))
precondition(wrongClamp(0) != 0)""",
            observe="Comparing wrongClamp(0) with itself passes, while comparing it with the literal 0 exposes the defect.",
            explain="A test whose two sides call the same code can never fail, so it proves nothing; the expected side must come from an independent oracle such as a literal derived from the rule.",
        ),
        5: dict(
            code=r"""func clampAll(_ texts: [String]) -> [Int]? {
  var result: [Int] = []
  for text in texts {
    guard let value = Int(text) else { return nil }
    result.append(max(0, value))
  }
  return result
}
precondition(clampAll([]) == [])
precondition(clampAll(["-1", "-1"]) == [0, 0])
precondition(clampAll(["2", "x"]) == nil)""",
            observe="Empty input gives [], duplicates keep both entries as [0, 0], and a malformed entry makes the whole result nil.",
            explain="Separate checks name separate contracts: empty is not an error, duplicates are preserved rather than merged, and malformed text is rejected rather than clamped.",
        ),
    },
    28: {
        1: dict(
            code=r"""func square(_ value: Int) async -> Int { value * value }
let first = await square(2)
let second = await square(3)
precondition(first + second == 13)
async let left = square(4)
async let right = square(5)
let both = await left + right
precondition(both == 41)""",
            observe="The two awaited calls give 4 + 9 = 13 one after another, and the async let pair gives 16 + 25 = 41.",
            explain="Marking square async only allows it to suspend; consecutive awaits still run in sequence. Concurrency appears only when async let creates child tasks that may overlap.",
        ),
        2: dict(
            code=r"""func double(_ value: Int) async -> Int { value * 2 }
let once = await double(4)
let twice = await double(once)
precondition(once == 8 && twice == 16)""",
            observe="The first await gives 8, and feeding it into the second gives 16.",
            explain="The second call needs the first result, so it must await in order; there is nothing to run in parallel when one step depends on another.",
        ),
        4: dict(
            explain="A semaphore wait blocks its thread until signaled. If the async work it waits for needs that same executor (for example the main actor or a one-thread pool), the work can never run to signal, and the program deadlocks. In an async context, await the work instead; the entry point here is already async, so no blocking bridge is needed.",
        ),
        5: dict(
            code=r"""func validated(_ value: Int) async throws -> Int {
  guard value >= 0 else { throw AsyncError.invalid }
  return value
}
let zero = try await validated(0)
precondition(zero == 0)
var failed = false
do { _ = try await validated(-5) } catch AsyncError.invalid { failed = true }
precondition(failed)""",
            observe="0 is accepted as the boundary value, and -5 throws AsyncError.invalid.",
            explain="try await checks both effects at the call site: suspension for async and propagation for throws, so the failure reaches the caller's catch unchanged.",
        ),
    },
    29: {
        1: dict(
            code=r"""let values = await withTaskGroup(of: Int.self, returning: [Int].self) { group in
  for value in [1, 2, 3] { group.addTask { value * 2 } }
  var owned: [Int] = []
  for await result in group { owned.append(result) }
  return owned
}
precondition(values.count == 3 && values.sorted() == [2, 4, 6])""",
            observe="The group returns three results that sort to [2, 4, 6].",
            explain="The group owns the three child tasks and does not return until they finish; each child owns only its copy of value, and only the parent closure owns and appends to the array.",
        ),
        2: dict(
            code=r"""let inputs = [3, 1, 2]
let ordered = await withTaskGroup(of: (Int, Int).self, returning: [Int].self) { group in
  for (index, value) in inputs.enumerated() { group.addTask { (index, value * 2) } }
  var pairs: [(Int, Int)] = []
  for await pair in group { pairs.append(pair) }
  return pairs.sorted { $0.0 < $1.0 }.map { $0.1 }
}
precondition(ordered == [6, 2, 4])""",
            observe="Tagging each child with its input index restores submission order: [6, 2, 4].",
            explain="Completion order is unspecified, and sorting by value would give [2, 4, 6]; sorting by the carried index reconstructs the order the inputs were submitted.",
        ),
        4: dict(
            code=r"""let doubled = await withTaskGroup(of: Int.self, returning: [Int].self) { group in
  for value in [4, 5] { group.addTask { value * 2 } }
  var results: [Int] = []
  for await result in group { results.append(result) }
  return results.sorted()
}
precondition(doubled == [8, 10])""",
            observe="Children return their values and the parent alone appends them, giving [8, 10].",
            explain="Appending to a shared var from inside addTask is rejected in Swift 6 as mutation of a captured var in concurrently-executing code, because two children could write at once. Returning values moves every write to the single owner.",
        ),
        5: dict(
            code=r"""enum ChildError: Error { case failed }
let empty = try await withThrowingTaskGroup(of: Int.self, returning: Int.self) { group in
  var total = 0
  for try await value in group { total += value }
  return total
}
precondition(empty == 0)
var failed = false
do {
  _ = try await withThrowingTaskGroup(of: Int.self, returning: Int.self) { group in
    for value in [1, 2, 3] {
      group.addTask {
        if value == 2 { throw ChildError.failed }
        return value
      }
    }
    var total = 0
    for try await value in group { total += value }
    return total
  }
} catch ChildError.failed {
  failed = true
}
precondition(failed)""",
            observe="An empty throwing group returns 0, and the child that throws on 2 makes the whole group throw ChildError.failed.",
            explain="for try await rethrows the first child error, and leaving the group by throwing cancels and awaits the remaining children, so no partial total escapes.",
        ),
    },
    30: {
        1: dict(
            code=r"""let task = Task { () -> String in
  while !Task.isCancelled { await Task.yield() }
  return "acknowledged"
}
precondition(!task.isCancelled)
task.cancel()
precondition(task.isCancelled)
let reply = await task.value
precondition(reply == "acknowledged")""",
            observe="isCancelled flips to true as soon as cancel() is called, but the result acknowledged arrives only after awaiting value.",
            explain="cancel() only records a request; the task observes it at its own check and finishes, and awaiting value is what confirms that completion.",
        ),
        2: dict(
            code=r"""func commit(_ log: [String]) async -> [String] {
  if Task.isCancelled { return log + ["skipped write"] }
  return log + ["wrote"]
}
let task = Task { () -> [String] in
  while !Task.isCancelled { await Task.yield() }
  return await commit(["read"])
}
task.cancel()
let cancelledLog = await task.value
precondition(cancelledLog == ["read", "skipped write"])
let normalLog = await commit(["read"])
precondition(normalLog == ["read", "wrote"])""",
            observe="The cancelled task records read then skipped write, while an uncancelled call records read then wrote.",
            explain="Checking Task.isCancelled immediately before the state-changing step stops the write when cancellation has been requested, while the earlier read is left as it was.",
        ),
        4: dict(
            explain="Cancelling the waiter stops the caller from waiting; it does not tell you whether the write reached the store. The outcome is unknown, so a blind retry can apply the write twice. Retry only with the same operation identity against a store that deduplicates it, or first query whether that identity was committed.",
        ),
        5: dict(
            code=r"""let started = await withTaskGroup(of: Int.self, returning: Bool.self) { group in
  group.cancelAll()
  return group.addTaskUnlessCancelled { 1 }
}
precondition(!started)
let finished = Task { 5 }
let first = await finished.value
finished.cancel()
let again = await finished.value
precondition(first == 5 && again == 5)""",
            observe="Cancelling first means the child is never started, while cancelling an already finished task still returns 5.",
            explain="addTaskUnlessCancelled refuses work once the group is cancelled; a completed task's result is fixed, so a late cancel has nothing to stop.",
        ),
    },
    31: {
        1: dict(
            code=r"""let inventory = InventoryActor(stock: 3)
let before = await inventory.stock
let reserved = await inventory.reserve(1)
let after = await inventory.stock
precondition(before == 3 && reserved && after == 2)""",
            observe="The outside reads of stock and the reserve call each need await, and stock goes from 3 to 2.",
            explain="stock is actor-isolated, so every outside read is an await; inside reserve, the guard read and the subtraction run on the actor without suspension, forming one serialized step.",
        ),
        2: dict(
            helpers=r"""struct StockSnapshot: Sendable, Equatable {
  let stock: Int
}
extension InventoryActor {
  func snapshot() -> StockSnapshot { StockSnapshot(stock: stock) }
}""",
            code=r"""let inventory = InventoryActor(stock: 3)
let before = await inventory.snapshot()
_ = await inventory.reserve(2)
let after = await inventory.snapshot()
precondition(before == StockSnapshot(stock: 3) && after.stock == 1)""",
            observe="The snapshot taken before the reservation still says 3, and a later one says 1.",
            explain="snapshot returns a Sendable value copy, so the caller holds a stable record that later actor changes cannot alter.",
        ),
        4: dict(
            code=r"""actor SplitInventory {
  private(set) var stock = 2
  func canReserve(_ amount: Int) -> Bool { amount <= stock }
  func subtract(_ amount: Int) { stock -= amount }
}
let split = SplitInventory()
let firstCheck = await split.canReserve(2)
let secondCheck = await split.canReserve(2)
await split.subtract(2)
await split.subtract(2)
let leftover = await split.stock
precondition(firstCheck && secondCheck && leftover == -2)
let safe = InventoryActor(stock: 2)
let one = await safe.reserve(2)
let two = await safe.reserve(2)
precondition(one && !two)""",
            observe="Two callers both pass the separate check and stock falls to -2; InventoryActor rejects the second reservation.",
            explain="Each actor call is serialized, but the await between check and subtract lets other work interleave. Keeping the check and the write in one actor method with no await inside removes the gap.",
        ),
        5: dict(
            code=r"""let inventory = InventoryActor(stock: 3)
let zero = await inventory.reserve(0)
let excess = await inventory.reserve(4)
let exact = await inventory.reserve(3)
let remaining = await inventory.stock
precondition(zero && !excess && exact && remaining == 0)""",
            observe="Reserving 0 succeeds, 4 is refused, and exactly 3 succeeds and leaves 0.",
            explain="The guard admits amounts from 0 through stock inclusive, so only the excess request fails and it changes nothing.",
        ),
    },
    32: {
        1: dict(
            code=r"""let ledger = ImportLedger()
let firstReceipt = try await ledger.apply(id: "a", amount: 5)
let afterFirst = await ledger.total
let repeatReceipt = try await ledger.apply(id: "a", amount: 5)
let afterRepeat = await ledger.total
precondition(firstReceipt == 5 && afterFirst == 5)
precondition(repeatReceipt == 5 && afterRepeat == 5)""",
            observe="The first call adds 5 and returns receipt 5; the repeat returns receipt 5 and the total stays 5.",
            explain="The first call finds no record, adds to the total and stores the pair; the repeat finds the matching record and returns its stored receipt without touching the total.",
        ),
        2: dict(
            code=r"""let ledger = ImportLedger()
_ = try await ledger.apply(id: "one", amount: 3)
let receipt = try await ledger.apply(id: "two", amount: 4)
let total = await ledger.total
precondition(receipt == 7 && total == 7)""",
            observe="Applying two with 4 after one with 3 returns receipt 7 and a total of 7.",
            explain="A new identity has no record, so its effect is applied and its receipt is the running total after the addition.",
        ),
        4: dict(
            code=r"""actor CarelessLedger {
  private var receipts: [String: Int] = [:]
  private(set) var total = 0
  func apply(id: String, amount: Int) -> Int {
    total += amount
    if let receipt = receipts[id] { return receipt }
    receipts[id] = total
    return total
  }
}
let careless = CarelessLedger()
_ = await careless.apply(id: "one", amount: 3)
_ = await careless.apply(id: "one", amount: 3)
let carelessTotal = await careless.total
let ledger = ImportLedger()
_ = try await ledger.apply(id: "one", amount: 3)
_ = try await ledger.apply(id: "one", amount: 3)
let safeTotal = await ledger.total
precondition(carelessTotal == 6 && safeTotal == 3)""",
            observe="Applying first and checking later doubles the replayed effect to 6; ImportLedger stays at 3.",
            explain="The careless ledger returns the old receipt, so the caller believes nothing happened while the total was already changed. The identity lookup must come before any effect.",
        ),
        5: dict(
            code=r"""let ledger = ImportLedger()
var invalid = false
do { _ = try await ledger.apply(id: "neg", amount: -1) } catch LedgerError.invalid {
  invalid = true
}
precondition(invalid)
let receipts = try await withThrowingTaskGroup(of: Int.self, returning: [Int].self) { group in
  for _ in 0..<5 { group.addTask { try await ledger.apply(id: "same", amount: 2) } }
  var collected: [Int] = []
  for try await receipt in group { collected.append(receipt) }
  return collected
}
let total = await ledger.total
precondition(receipts == [2, 2, 2, 2, 2] && total == 2)""",
            observe="A negative amount throws invalid, and five concurrent identical requests all receive receipt 2 while the total stays 2.",
            explain="The actor runs each apply to completion without suspension, so only the first request applies the effect and the other four find its record.",
        ),
    },
    33: {
        1: dict(
            code=r"""let snapshot = Snapshot(name: "pear", quantity: 3)
let task = Task { Snapshot(name: snapshot.name, quantity: snapshot.quantity * 2) }
let doubled = await task.value
precondition(snapshot.quantity == 3)
precondition(doubled.name == "pear" && doubled.quantity == 6)""",
            observe="The parent's snapshot still holds 3, and the task hands back a new snapshot holding 6.",
            explain="The parent owns snapshot and the task receives an immutable copy; the task owns the value it builds until it returns, and then the awaiting parent owns the result.",
        ),
        2: dict(
            code=r"""struct PricedSnapshot: Sendable {
  let name: String
  let quantity: Int
  let unitPrice: Int
}
let snapshot = PricedSnapshot(name: "pear", quantity: 3, unitPrice: 4)
let cost = await Task { snapshot.quantity * snapshot.unitPrice }.value
precondition(cost == 12)""",
            observe="With an added unitPrice of 4, the task computes a cost of 12 from 3 pears.",
            explain="A struct whose stored properties are all let and themselves Sendable stays Sendable, so the new field crosses the task boundary without any extra synchronization.",
        ),
        4: dict(
            code=r"""actor Tally {
  private(set) var count = 0
  func add() { count += 1 }
}
let tally = Tally()
await withTaskGroup(of: Void.self) { group in
  for _ in 0..<100 { group.addTask { await tally.add() } }
}
let count = await tally.count
precondition(count == 100)""",
            observe="One hundred concurrent increments through the actor produce exactly 100.",
            explain="Marking a class with a mutable var as @unchecked Sendable silences the compiler without adding any lock, so concurrent increments can be lost. Moving the state into an actor makes the compiler enforce serialized access instead.",
        ),
        5: dict(
            code=r"""let none = await withTaskGroup(of: Snapshot.self, returning: [Snapshot].self) { group in
  var collected: [Snapshot] = []
  for await value in group { collected.append(value) }
  return collected
}
precondition(none.isEmpty)
let many = await withTaskGroup(of: Snapshot.self, returning: [String].self) { group in
  for number in 1...4 { group.addTask { Snapshot(name: "p\(number)", quantity: number) } }
  var names: [String] = []
  for await value in group { names.append(value.name) }
  return names.sorted()
}
precondition(many == ["p1", "p2", "p3", "p4"])""",
            observe="A group with no producers returns no snapshots, and four producers yield p1 through p4 once sorted.",
            explain="The parent alone appends and sorts, so the result is deterministic regardless of which producer finishes first, and the empty case needs no special handling.",
        ),
    },
    34: {
        1: dict(
            code=r"""let (stream, continuation) = AsyncStream<Int>.makeStream(bufferingPolicy: .bufferingNewest(5))
var buffered = -1
if case .enqueued(let remaining) = continuation.yield(2) { buffered = remaining }
precondition(buffered == 4)
continuation.finish()
var terminated = false
if case .terminated = continuation.yield(9) { terminated = true }
precondition(terminated)
var values: [Int] = []
for await value in stream { values.append(value) }
precondition(values == [2])""",
            observe="Yielding 2 reports 4 free buffer slots, a yield after finish reports terminated, and the consumer receives only [2].",
            explain="The producer yields into the buffer before anyone reads, finish marks completion, and later yields are refused; the consumer drains the buffer and its loop ends at the finish.",
        ),
        2: dict(
            code=r"""let stream = AsyncStream<Int>(bufferingPolicy: .bufferingOldest(1)) { continuation in
  continuation.yield(1)
  continuation.yield(2)
  continuation.finish()
}
var values: [Int] = []
for await value in stream { values.append(value) }
precondition(values == [1])""",
            observe="With bufferingOldest(1), the stream keeps 1 and drops 2.",
            explain="The oldest policy keeps what is already buffered and discards new arrivals when full, the opposite of bufferingNewest, which kept 2.",
        ),
        4: dict(
            code=r"""let (stream, continuation) = AsyncStream<Int>.makeStream()
continuation.yield(1)
continuation.yield(2)
continuation.finish()
var count = 0
for await _ in stream { count += 1 }
precondition(count == 2)""",
            observe="After two values and finish, the loop counts 2 and ends.",
            explain="for await only ends when the stream finishes; without continuation.finish() the consumer would wait forever after 2, so the owner of a finite producer must finish it on every path.",
        ),
        5: dict(
            code=r"""let (empty, emptyContinuation) = AsyncStream<Int>.makeStream()
emptyContinuation.finish()
var none: [Int] = []
for await value in empty { none.append(value) }
precondition(none.isEmpty)
let (stream, continuation) = AsyncStream<Int>.makeStream(bufferingPolicy: .bufferingOldest(2))
continuation.yield(1)
continuation.yield(2)
var dropped: Int?
if case .dropped(let value) = continuation.yield(3) { dropped = value }
continuation.finish()
var kept: [Int] = []
for await value in stream { kept.append(value) }
precondition(dropped == 3 && kept == [1, 2])""",
            observe="A stream finished with no events yields nothing; with room for two, the third yield reports dropped 3 and the consumer gets [1, 2].",
            explain="The yield result makes the overflow policy observable at the producer, so dropped work can be counted or logged rather than vanishing silently.",
        ),
    },
    35: {
        1: dict(
            code=r"""let values = [2, 3, 4]
let byteCount = values.withUnsafeBytes { bytes in bytes.count }
precondition(byteCount == values.count * MemoryLayout<Int>.stride)
let total = values.withUnsafeBufferPointer { buffer in buffer.reduce(0, +) }
precondition(total == 9)""",
            observe="The raw view spans 3 times the Int stride in bytes, and the buffer sums to 9.",
            explain="Each pointer is valid only inside its closure; what leaves the call is an owned Int (the byte count or the total), never the pointer itself.",
        ),
        2: dict(
            code=r"""func largest(_ values: [Int]) -> Int? {
  values.withUnsafeBufferPointer { buffer in
    guard let first = buffer.first else { return nil }
    return buffer.reduce(first, max)
  }
}
precondition(largest([]) == nil)
precondition(largest([3, 9, 2]) == 9)""",
            observe="The empty array gives nil, and [3, 9, 2] gives 9.",
            explain="An empty buffer has no maximum, so the contract returns nil instead of reading a nonexistent first element or inventing a sentinel.",
        ),
        4: dict(
            code=r"""let values = [5, 6]
let copied = values.withUnsafeBufferPointer { buffer in Array(buffer) }
precondition(copied == [5, 6])""",
            observe="Copying out of the buffer inside the closure returns an owned array [5, 6].",
            explain="Returning buffer.baseAddress hands out a pointer whose validity ends with the closure; using it later is undefined even if the address looks unchanged. Copy the needed data out while access is still granted.",
        ),
        5: dict(
            code=r"""func bufferSum(_ values: [Int]) -> Int {
  values.withUnsafeBufferPointer { buffer in buffer.reduce(0, +) }
}
precondition(bufferSum([]) == 0)
precondition(bufferSum([7]) == 7)
precondition(bufferSum([1, 2, 3, 4]) == 10)""",
            observe="The sums are 0 for empty, 7 for a single element, and 10 for four elements.",
            explain="reduce never dereferences an empty buffer, and the singleton case shows the loop runs exactly once; all three sizes use the same scoped access.",
        ),
    },
    36: {
        1: dict(
            code=r"""func comparisons(_ values: [Int], _ target: Int) -> Int {
  var count = 0
  for value in values {
    count += 1
    if value == target { break }
  }
  return count
}
let values = [2, 4, 6, 8]
precondition(comparisons(values, 2) == 1)
precondition(comparisons(values, 8) == 4)
precondition(comparisons(values, 9) == 4)""",
            observe="Finding the first element takes 1 comparison, the last takes 4, and an absent target also takes 4.",
            explain="A linear scan stops at a match, so its cost depends on position; an absent target is the worst case because every element must be checked.",
        ),
        2: dict(
            code=r"""func worstCase(_ values: [Int]) -> Int {
  var count = 0
  for value in values {
    count += 1
    if value == -1 { break }
  }
  return count
}
let small = [2, 4, 6, 8]
let large = small + [10, 12, 14, 16]
precondition(worstCase(small) == 4 && worstCase(large) == 8)""",
            observe="Doubling the input from 4 to 8 elements doubles the absent-target comparisons from 4 to 8.",
            explain="Worst-case linear search does one comparison per element, so its work grows in proportion to n.",
        ),
        4: dict(
            code=r"""let values = Array(1...1000)
var scanWork = 0
for value in values {
  scanWork += 1
  if value == 3 { break }
}
let index = Set(values)
let buildWork = values.count
precondition(index.contains(3) && scanWork == 3 && buildWork == 1000)""",
            observe="A single query for 3 scans 3 elements, while building the Set alone touches all 1,000.",
            explain="For one query, the index costs more to build than the scan it replaces; a benchmark that times only contains hides that cost, and building only pays off over many lookups.",
        ),
        5: dict(
            code=r"""let duplicates = [2, 2, 4]
precondition(Set(duplicates).count == 2 && duplicates.count == 3)
precondition(Set(duplicates).contains(2))
let empty: [Int] = []
precondition(!empty.contains(1) && Set(empty).isEmpty)""",
            observe="Three inputs with a repeated 2 give a Set of 2 members that still answers contains(2); the empty workload finds nothing.",
            explain="Set membership collapses duplicates, which preserves yes or no answers but not counts, and an empty input does no comparisons in either strategy.",
        ),
    },
    37: {
        1: dict(
            code=r"""let direct = Clamped(wrappedValue: 15, 0...10)
precondition(direct.wrappedValue == 10)
var control = Control()
precondition(control.level == 0)
control.level = 12
precondition(control.level == 10)
control.level = -2
precondition(control.level == 0)""",
            observe="Initializing with 15 already clamps to 10, Control starts at 0, and the two setters store 10 then 0.",
            explain="@Clamped(0...10) var level = 0 calls init(wrappedValue: 0, 0...10), which clamps once; each later assignment goes through the wrappedValue setter, which clamps again.",
        ),
        2: dict(
            code=r"""struct Volume {
  @Clamped(1...5) var level = 3
}
var volume = Volume()
volume.level = 0
precondition(volume.level == 1)
volume.level = 6
precondition(volume.level == 5)
precondition(volume.$level == 1...5)""",
            observe="With range 1...5, 0 becomes 1, 6 becomes 5, and the projection reports 1...5.",
            explain="The range is a wrapper argument, so changing it moves both boundaries and the tests must move with it; the projection lets the test read the active range.",
        ),
        4: dict(
            code=r"""struct Payment {
  @Clamped(0...100) var amount = 0
}
var payment = Payment()
payment.amount = 250
precondition(payment.amount == 100)
enum AmountError: Error { case outOfRange }
func checkedAmount(_ value: Int) throws -> Int {
  guard (0...100).contains(value) else { throw AmountError.outOfRange }
  return value
}
precondition((try? checkedAmount(250)) == nil)""",
            observe="The clamped payment silently becomes 100, while the checked version refuses 250.",
            explain="Clamping a payment changes what the user asked to pay without telling them; a failure that can be reported is the honest result for money.",
        ),
        5: dict(
            code=r"""var control = Control()
control.level = 0
precondition(control.level == 0)
control.level = 10
precondition(control.level == 10)
control.level = -1
precondition(control.level == 0)
control.level = 11
precondition(control.level == 10)""",
            observe="The endpoints 0 and 10 are kept, -1 becomes 0, and 11 becomes 10.",
            explain="The range is closed, so both endpoints are valid stored values; one step past either end is pulled back to that endpoint.",
        ),
    },
    38: {
        1: dict(
            code=r"""let manual = SectionBuilder.buildBlock(
  SectionBuilder.buildExpression("Overview"),
  SectionBuilder.buildExpression("Details"))
let built = sections {
  "Overview"
  "Details"
}
precondition(manual == built && manual == ["Overview", "Details"])""",
            observe="Calling buildExpression on each string and passing both to buildBlock gives the same [Overview, Details] as the builder block.",
            explain="The compiler rewrites each expression statement into buildExpression and combines the results with buildBlock, which flattens the one-element arrays in order.",
        ),
        2: dict(
            code=r"""let include = false
let report = sections {
  "Overview"
  if include { "Diagnostics" }
}
precondition(report == ["Overview"])""",
            observe="With include set to false, the report is just [Overview].",
            explain="A false if passes nil to buildOptional, which returns an empty array, so the conditional contributes nothing.",
        ),
        4: dict(
            helpers=r"""@resultBuilder enum LoopingSectionBuilder {
  static func buildExpression(_ value: String) -> [String] { [value] }
  static func buildBlock(_ components: [String]...) -> [String] { components.flatMap { $0 } }
  static func buildArray(_ components: [[String]]) -> [String] { components.flatMap { $0 } }
}
func loopingSections(@LoopingSectionBuilder _ content: () -> [String]) -> [String] { content() }""",
            code=r"""let names = ["North", "South"]
let report = loopingSections {
  "Overview"
  for name in names { "Region \(name)" }
}
precondition(report == ["Overview", "Region North", "Region South"])""",
            observe="With buildArray available, the loop contributes Region North and Region South after Overview.",
            explain="SectionBuilder has no buildArray, so swiftc rejects a for-in loop inside sections; the loop is legal only once the builder says how to combine one result per iteration.",
        ),
        5: dict(
            code=r"""let empty = sections {}
precondition(empty.isEmpty)
let show = false
let hidden = sections {
  if show { "Hidden" }
}
precondition(hidden.isEmpty)""",
            observe="An empty block and a block with only a false conditional both produce [].",
            explain="buildBlock with no components flattens to an empty array, and buildOptional(nil) also returns []; neither case needs a special path.",
        ),
    },
    39: {
        1: dict(
            code=r"""let item = PlannerItem(id: "one", title: "Read", completed: false)
let updated = toggled(item)
let rowText = "\(updated.title): \(updated.completed ? "done" : "open")"
precondition(updated.completed && rowText == "Read: done")""",
            observe="The domain step flips completion, and a separate presentation step renders Read: done.",
            explain="toggled is domain logic: it decides what completing an item means and knows nothing about text or views. Turning the value into Read: done is presentation, which can change without touching the rule.",
        ),
        2: dict(
            code=r"""enum RenameError: Error { case emptyTitle }
func renamed(_ item: PlannerItem, to title: String) throws -> PlannerItem {
  let trimmed = title.trimmingCharacters(in: .whitespacesAndNewlines)
  guard !trimmed.isEmpty else { throw RenameError.emptyTitle }
  return PlannerItem(id: item.id, title: trimmed, completed: item.completed)
}
let item = PlannerItem(id: "one", title: "Read", completed: true)
let changed = try renamed(item, to: " Review ")
precondition(changed.id == "one" && changed.title == "Review" && changed.completed)
precondition((try? renamed(item, to: "   ")) == nil)""",
            observe="Renaming to padded Review keeps id one and completion, while a blank title is refused.",
            explain="The rename is pure: it returns a new value and keeps identity, and the rule that titles are nonempty lives in the domain, so every caller gets the same refusal.",
        ),
        3: dict(
            explain="Copy fixtures/JourneyCore into your own workspace and run swift build and then swift test there before touching JourneyApp. In the reference run on swift:6.3.3-noble the build ended with Build complete! and the test run reported Executed 4 tests, with 0 failures. A green core is the precondition for the app, but it says nothing yet about rendering or navigation.",
        ),
        4: dict(
            code=r"""struct PlanSnapshot {
  let titles: [String]
  var count: Int { titles.count }
}
func loadPlan(from storage: [String: [String]], key: String) -> PlanSnapshot {
  PlanSnapshot(titles: storage[key] ?? [])
}
let storage = ["plan": ["Read", "Practice"]]
let plan = loadPlan(from: storage, key: "plan")
precondition(plan.count == 2 && plan.count == 2)""",
            observe="The plan is loaded once by an adapter, and reading count twice is a plain computation returning 2 each time.",
            explain="A getter that reads a file runs I/O on every access, can fail with nowhere to report the error, and hides cost behind property syntax. Loading belongs to an adapter that returns a value; model properties then stay pure and cheap.",
        ),
        5: dict(
            code=r"""enum AdmitError: Error { case duplicate, unknown }
func admit(_ item: PlannerItem, into items: [PlannerItem]) throws -> [PlannerItem] {
  guard !items.contains(where: { $0.id == item.id }) else { throw AdmitError.duplicate }
  return items + [item]
}
func toggle(id: String, in items: [PlannerItem]) throws -> [PlannerItem] {
  guard let index = items.firstIndex(where: { $0.id == id }) else { throw AdmitError.unknown }
  var result = items
  result[index] = toggled(result[index])
  return result
}
let items = try admit(PlannerItem(id: "a", title: "Read", completed: false), into: [])
precondition(
  (try? admit(PlannerItem(id: "a", title: "Copy", completed: false), into: items)) == nil)
precondition((try? toggle(id: "missing", in: items)) == nil)
let toggledItems = try toggle(id: "a", in: items)
precondition(toggledItems[0].completed)""",
            observe="A second item with id a is refused, toggling an unknown id fails, and toggling a succeeds.",
            explain="Both rules are checked in the domain before anything changes, so a duplicate cannot slip in and an unknown id cannot silently do nothing.",
        ),
    },
    40: {
        1: dict(
            code=r"""var state = FormState(title: "Read", completed: false)
precondition(state.buttonLabel == "Mark complete")
state.completed.toggle()
precondition(state.buttonLabel == "Mark incomplete")""",
            observe="Toggling the stored completed flag changes the derived label from Mark complete to Mark incomplete.",
            explain="title and completed are stored; buttonLabel is computed from completed every time it is read, so it can never disagree with the state it describes.",
        ),
        2: dict(
            code=r"""struct EditableForm {
  var title: String
  var completed: Bool
  var saveDisabled: Bool { title.trimmingCharacters(in: .whitespaces).isEmpty }
}
var form = EditableForm(title: "Read", completed: false)
precondition(!form.saveDisabled)
form.title = "  "
precondition(form.saveDisabled)""",
            observe="Save is enabled for Read and disabled once the title is only spaces.",
            explain="saveDisabled is derived from title rather than stored, so no code path can forget to update it; the domain must still reject a blank title on its own.",
        ),
        3: dict(
            explain="This task needs a prepared Mac and was not run for this reference. Generate and run JourneyApp as its README describes, add an item, open it and change the title. ItemEditor binds its TextField to a local @State draft, so typing changes only the draft; Save changes calls store.update, which writes through StudyPlan.update and publishes the new title to the list. Cancel dismisses without calling update, so the list keeps the old title.",
        ),
        4: dict(
            code=r"""final class Model { var title = "Read" }
struct StaleChild {
  var copy: String
  init(model: Model) { copy = model.title }
}
struct LiveChild {
  let model: Model
  var shown: String { model.title }
}
let model = Model()
let stale = StaleChild(model: model)
let live = LiveChild(model: model)
model.title = "Review"
precondition(stale.copy == "Read" && live.shown == "Review")""",
            observe="After the parent changes the title, the copying child still shows Read while the reading child shows Review.",
            explain="Copying input into the child's own state at creation freezes it; later parent updates never arrive. Read from the shared source, or use a binding, unless the copy is a deliberate draft.",
        ),
        5: dict(
            code=r"""struct Draft {
  var title: String
  func commit(into saved: inout String) { saved = title }
}
var saved = "Read"
var edit = Draft(title: saved)
edit.title = "Review"
edit.commit(into: &saved)
precondition(saved == "Review")
var cancelled = Draft(title: saved)
cancelled.title = "Discard me"
precondition(saved == "Review")""",
            observe="A committed edit changes the saved title to Review, and a cancelled draft leaves it unchanged on return to the list.",
            explain="This portable kernel mirrors ItemEditor's draft contract: edits stay in a draft until an explicit save. The real return to the list must still be checked in JourneyApp on an Apple destination.",
        ),
    },
    41: {
        1: dict(
            code=r"""let parts = URLComponents(string: "journey://item/one")!
precondition(parts.scheme == "journey" && parts.host == "item" && parts.path == "/one")
precondition(parts.query == nil && parts.fragment == nil)
precondition(parseRoute("journey://item/one?x=1") == nil)
precondition(parseRoute("journey://item/one/two") == nil)""",
            observe="The scheme, host and one path segment admit the link, while an added query or a second path segment rejects it.",
            explain="Each component is a separate gate: scheme and host pick the route family, query and fragment must be absent, and the path must hold exactly one identity segment.",
        ),
        2: dict(
            code=r"""enum AppRoute: Equatable {
  case overview
  case item(String)
}
func parseAppRoute(_ text: String) -> AppRoute? {
  guard let url = URLComponents(string: text), url.scheme == "journey", url.query == nil,
    url.fragment == nil
  else { return nil }
  let parts = url.path.split(separator: "/")
  switch (url.host, parts.count) {
  case ("overview"?, 0): return .overview
  case ("item"?, 1): return .item(String(parts[0]))
  default: return nil
  }
}
precondition(parseAppRoute("journey://overview") == .overview)
precondition(parseAppRoute("journey://overview/extra") == nil)
precondition(parseAppRoute("journey://item/one") == .item("one"))""",
            observe="journey://overview becomes the overview route, an overview with a path is rejected, and item links still work.",
            explain="The overview is its own explicit case with its own shape rule, rather than a special value of item, so each accepted link has exactly one meaning.",
        ),
        3: dict(
            explain="This task needs a prepared Mac and was not run for this reference. In JourneyApp, each row is NavigationLink(value: item.id), and navigationDestination(for: String.self) looks the id up in store.plan.items. Add two items, open one, go back, add another and reopen: the editor always shows the item whose id was pushed, not whatever now sits at that row position.",
        ),
        4: dict(
            code=r"""let items = ["a": "Read", "b": "Practice"]
var order = ["a", "b"]
let selectedIndex = 0
let selectedID = order[selectedIndex]
order.reverse()
precondition(items[order[selectedIndex]] == "Practice")
precondition(items[selectedID] == "Read")""",
            observe="After reordering, position 0 now names Practice, while the stored id still names Read.",
            explain="An array offset identifies a slot, not an item; reordering, inserting or deleting moves a different item into the slot. Navigating by stable id keeps the route attached to the same item.",
        ),
        5: dict(
            code=r"""precondition(parseRoute("journey://item/") == nil)
var items = ["one": "Read"]
let route = parseRoute("journey://item/one")
items["one"] = nil
var screen = "none"
if case .item(let id)? = route { screen = items[id] ?? "Item unavailable" }
precondition(screen == "Item unavailable")""",
            observe="A link with no identity is rejected, and a route to an item deleted while open resolves to Item unavailable.",
            explain="The route stays valid as syntax, but the lookup happens at display time, so a deleted item gets an explicit unavailable screen, which matches the ContentUnavailableView in JourneyApp.",
        ),
    },
    42: {
        1: dict(
            code=r"""let future = Data(#"{"schemaVersion":99,"titles":["Keep"]}"#.utf8)
let decoded = try JSONDecoder().decode(SavedPlan.self, from: future)
precondition(decoded.schemaVersion == 99 && !supported(decoded))
let blank = SavedPlan(schemaVersion: 1, titles: [""])
precondition(!supported(blank))""",
            observe="A version 99 document decodes as JSON but is unsupported, and a version 1 document with a blank title is also refused.",
            explain="Decoding only checks shape; the version gate and the nonempty-title rule are separate checks applied afterward, which is why both documents parse yet neither is accepted.",
        ),
        2: dict(
            code=r"""struct SavedPlanWithNote: Codable {
  let schemaVersion: Int
  let titles: [String]
  let note: String?
}
let old = Data(#"{"schemaVersion":1,"titles":["Read"]}"#.utf8)
let decoded = try JSONDecoder().decode(SavedPlanWithNote.self, from: old)
precondition(decoded.note == nil && decoded.titles == ["Read"])""",
            observe="An old version 1 document without note still decodes, with note set to nil.",
            explain="Synthesized decoding treats an optional property as absent-means-nil, so adding an optional field stays compatible with files written before it existed.",
        ),
        3: dict(
            explain="The full app check needs a prepared Mac and was not run here. PlanStore decodes plan.json through StudyPlan.decode; on failure it sets persistenceBlocked, keeps the file, and shows The saved plan could not be loaded. A reference JourneyCore test on swift:6.3.3-noble confirmed the inputs: empty and truncated data threw DecodingError, and schemaVersion 2 threw unsupportedVersion. Test with a copy in your own directory, never with your only saved plan.",
        ),
        4: dict(
            code=r"""enum LoadResult: Equatable {
  case loaded([String])
  case blocked(original: Data)
}
func load(_ data: Data) -> LoadResult {
  guard let plan = try? JSONDecoder().decode(SavedPlan.self, from: data), supported(plan)
  else { return .blocked(original: data) }
  return .loaded(plan.titles)
}
let unreadable = Data("{".utf8)
precondition(load(unreadable) == .blocked(original: unreadable))""",
            observe="An unreadable file produces blocked with the original bytes kept, instead of an empty plan.",
            explain="Replacing an unreadable file with an empty default looks like a fresh start, but the next save overwrites the user's only copy. Blocking writes and keeping the original leaves recovery possible.",
        ),
        5: dict(
            code=r"""let decoder = JSONDecoder()
precondition((try? decoder.decode(SavedPlan.self, from: Data())) == nil)
precondition((try? decoder.decode(SavedPlan.self, from: Data("[1,".utf8))) == nil)
let future = try decoder.decode(
  SavedPlan.self, from: Data(#"{"schemaVersion":2,"titles":[]}"#.utf8))
precondition(!supported(future))""",
            observe="Empty data and malformed JSON both fail to decode, while a version 2 document decodes but is unsupported.",
            explain="The three cases fail at different layers, so each gets its own check: empty and malformed data fail in decoding, and the future version fails in the version policy.",
        ),
    },
    43: {
        1: dict(
            code=r"""var state = LoadState(generation: 1, title: nil)
state.generation += 1
state.accept("first", generation: 1)
precondition(state.title == nil)
state.accept("second", generation: 2)
precondition(state.title == "second")""",
            observe="After intent moves to generation 2, the reply tagged 1 is ignored and the reply tagged 2 is shown.",
            explain="generation records the current intent, and each reply carries the generation of the request that produced it; only a matching pair may change the visible title.",
        ),
        2: dict(
            code=r"""var state = LoadState(generation: 3, title: "three")
state.generation = 4
state.accept("late three", generation: 3)
state.accept("four", generation: 4)
precondition(state.title == "four")""",
            observe="After advancing to generation 4, the late reply for 3 is dropped and four is accepted.",
            explain="Advancing the generation when a new request starts makes every older in-flight reply stale at once, without having to cancel each one first.",
        ),
        3: dict(
            helpers=r"""struct TransportResponse: Sendable {
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
}""",
            code=r"""let fake = FakeTransport(responses: [
  "/ok": TransportResponse(status: 200, body: Data("Read".utf8)),
  "/down": TransportResponse(status: 503, body: Data()),
])
let title = try await loadTitle("/ok", using: fake)
precondition(title == "Read")
var failure: TitleLoadError?
do { _ = try await loadTitle("/down", using: fake) } catch let error as TitleLoadError {
  failure = error
}
precondition(failure == .status(503))""",
            observe="The fake returns Read for /ok and a status 503 failure for /down, the same way on every run.",
            explain="The loader depends on a protocol, so a fixed table of responses replaces the network; success and failure are reproducible without sockets, timing or a server.",
        ),
        4: dict(
            code=r"""var state = LoadState(generation: 0, title: nil)
state.generation = 1
let oldQuery = state.generation
state.generation = 2
let newQuery = state.generation
state.accept("results for re", generation: newQuery)
state.accept("results for r", generation: oldQuery)
precondition(state.title == "results for re")""",
            observe="The slower reply for the old query arrives last but cannot overwrite results for re.",
            explain="Without a request identity, whichever reply finishes last wins, so a slow old search can replace a newer one. Tagging each reply with its generation lets late replies be dropped.",
        ),
        5: dict(
            code=r"""enum Outcome: Equatable {
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
precondition(cancelled)""",
            observe="Empty, malformed and 404 replies map to three different outcomes, and the cancelled request ends with CancellationError.",
            explain="Each case gets its own outcome so the UI can explain it, and cancellation is a separate path rather than a failure, which keeps a cancelled search from showing an error.",
        ),
    },
    44: {
        1: dict(
            code=r"""struct ColorOnlyRow {
  let title: String
  let tint: String
}
let row = ColorOnlyRow(title: "Read", tint: "green")
let spoken = row.title
precondition(!spoken.contains("complete"))
let labeled = "\(row.title), \(row.tint == "green" ? "complete" : "incomplete")"
precondition(labeled == "Read, complete")""",
            observe="With color alone, the spoken text is just Read; adding words produces Read, complete.",
            explain="Completion was carried only by tint, so anyone who cannot see the color loses it; the word complete survives screen readers, grayscale and color blindness.",
        ),
        2: dict(
            code=r"""func rowLabel(title: String, complete: Bool) -> String {
  "\(title), \(complete ? "complete" : "incomplete")"
}
func actionLabel(title: String, complete: Bool) -> String {
  complete ? "Mark \(title) incomplete" : "Mark \(title) complete"
}
precondition(rowLabel(title: "Read", complete: false) == "Read, incomplete")
precondition(actionLabel(title: "Read", complete: false) == "Mark Read complete")""",
            observe="The incomplete row reads Read, incomplete and its action reads Mark Read complete.",
            explain="The row label states the current state and the action label states what activating it will do, both naming the item so they make sense out of context.",
        ),
        3: dict(
            explain="This task needs a Mac with JourneyApp running and was not performed for this reference. Turn on VoiceOver and Full Keyboard Access, then move through the progress summary, the new item field, Add and each row. PlanView hides the decorative checkmark and gives each row the label title, complete or incomplete, so VoiceOver should say, for example, Read a chapter, incomplete. Record the actual focus order you hear.",
        ),
        4: dict(
            code=r"""let identifier = "row-7"
let label = "Read a chapter, incomplete"
precondition(!identifier.contains("Read") && label.contains("Read"))""",
            observe="The identifier row-7 tells the user nothing, while the label names the item and its state.",
            explain="accessibilityIdentifier exists for tests and is never spoken. If it is the only distinguishing text, VoiceOver users hear nothing useful. Keep the identifier for tests and add a real accessibilityLabel.",
        ),
        5: dict(
            explain="These checks need the Apple project on a prepared Mac and were not run for this reference. Set Dynamic Type to the largest accessibility size and confirm row text wraps instead of clipping; delete every item and confirm the list and progress text still make sense; then enter a very long title and confirm it wraps in the row and the editor. Note each failure with the setting that caused it.",
        ),
    },
    45: {
        1: dict(
            code=r"""var bridge = TextBridgeState(text: "", assignments: 0)
let renders = ["draft", "draft", "final"]
for value in renders { bridge.update(value) }
precondition(bridge.text == "final" && bridge.assignments == 2)""",
            observe="Three value-driven updates cause only two imperative assignments, ending at final.",
            explain="SwiftUI side: the struct describes a value and may be re-evaluated often. Imperative side: the platform view holds its own text and should be assigned only when the value actually changes.",
        ),
        2: dict(
            code=r"""var bridge = TextBridgeState(text: "same", assignments: 0)
bridge.update("same")
precondition(bridge.assignments == 0)
bridge.update("other")
precondition(bridge.assignments == 1)""",
            observe="Updating to the same text assigns nothing, and a real change assigns once.",
            explain="The guard compares first, so a re-render with an unchanged value leaves the platform view alone, which preserves selection and avoids extra delegate callbacks.",
        ),
        3: dict(
            explain="This task needs Xcode and was not run for this reference. SelectableText.swift wraps UITextView under canImport(UIKit) and NSTextField under canImport(AppKit). Build both schemes from the README: JourneyMac compiles only the AppKit branch and JourneyIOS only the UIKit branch. Each update method assigns text only when it differs, the same guard as the portable kernel.",
        ),
        4: dict(
            code=r"""var writes = 0
var value = "a"
func callback(_ incoming: String, depth: Int) {
  guard depth < 5 else { return }
  guard incoming != value else { return }
  value = incoming
  writes += 1
  callback(incoming, depth: depth + 1)
}
callback("b", depth: 0)
precondition(writes == 1 && value == "b")""",
            observe="With an equality guard, the echoed callback stops after one write.",
            explain="An update that writes the binding triggers another update, which writes again; with no change check it recurses or loops. Compare before writing so the echo becomes a no-op.",
        ),
        5: dict(
            code=r"""var bridge = TextBridgeState(text: "x", assignments: 0)
bridge.update("")
precondition(bridge.text.isEmpty && bridge.assignments == 1)
let large = String(repeating: "a", count: 100_000)
bridge.update(large)
bridge.update(large)
precondition(bridge.text.count == 100_000 && bridge.assignments == 2)""",
            observe="Empty text is assigned once, and a 100,000 character string repeated twice is assigned only once more.",
            explain="This checks the portable state rule. Scrolling, layout and memory with large text in the real UITextView or NSTextField still need the Apple project.",
        ),
    },
    46: {
        1: dict(
            explain="domain-tests shows that the rules in JourneyCore hold for the tested inputs. package-build shows that the package compiles with this toolchain. ui-tested would show that an automated script drove real screens, and device-signed that a signed build installed on hardware. Each proves only its own claim; none implies the others.",
        ),
        2: dict(
            code=r"""var observed: Set<String> = ["domain-tests", "ui-smoke"]
let saved = Data(#"{"titles":["Read"]}"#.utf8)
let reloaded = try JSONDecoder().decode([String: [String]].self, from: saved)
if reloaded["titles"] == ["Read"] { observed.insert("save-reload") }
let required: Set<String> = ["domain-tests", "ui-smoke", "save-reload"]
precondition(required.subtracting(observed).isEmpty)""",
            observe="save-reload is recorded only after the reload returns Read, and then no required gate is missing.",
            explain="The evidence is inserted as a consequence of a check that ran, not typed in by hand, so the set cannot claim a gate nobody performed.",
        ),
        3: dict(
            explain="This task needs Xcode and XcodeGen on a Mac and was not run for this reference. From your copy of JourneyApp run xcodegen generate --spec project.yml, xcodebuild -list, then xcodebuild -showdestinations for JourneyMac, and pick a destination that list actually shows. Run the test action on that destination; it should execute JourneySmokeTests.testAddItemUpdatesProgress. Record the Xcode version, destination and result.",
        ),
        4: dict(
            code=r"""let archiveEvidence: Set<String> = ["compiled", "archived"]
precondition(!archiveEvidence.contains("voiceover-checked"))""",
            observe="The archive evidence contains compiled and archived but nothing about VoiceOver.",
            explain="An archive proves the code compiled and was packaged. Screen-reader usability depends on labels, order and focus at run time, which only a person or a UI test using VoiceOver can observe.",
        ),
        5: dict(
            code=r"""var disk: [String: Data] = [:]
func launch() -> (titles: [String], blocked: Bool) {
  guard let data = disk["plan"] else { return ([], false) }
  guard let titles = try? JSONDecoder().decode([String].self, from: data) else { return ([], true) }
  return (titles, false)
}
precondition(launch().titles.isEmpty && !launch().blocked)
disk["plan"] = try JSONEncoder().encode(["Read"])
precondition(launch().titles == ["Read"])
disk["plan"] = Data("{".utf8)
precondition(launch().blocked && disk["plan"] == Data("{".utf8))""",
            observe="A fresh launch is empty, a saved plan reloads as Read, and malformed data blocks saving while its bytes stay on disk.",
            explain="This portable model follows PlanStore's policy. The same three launches still need checking in the real app on an Apple destination, using its --ui-testing directory and not your own data.",
        ),
    },
    47: {
        1: dict(
            code=r"""struct PortablePlan {
  let completed: Int
  let total: Int
  var summary: String { "\(completed)/\(total) complete" }
}
let plan = PortablePlan(completed: 1, total: 2)
precondition(plan.summary == "1/2 complete")""",
            observe="The summary 1/2 complete comes from a type that imports no UI framework.",
            explain="Counting, validation and summaries belong in the portable core because they behave the same everywhere. Views, platform bridges and file locations belong in the app targets.",
        ),
        2: dict(
            code=r"""func percentComplete(completed: Int, total: Int) -> Int {
  guard total > 0 else { return 0 }
  return completed * 100 / total
}
precondition(percentComplete(completed: 1, total: 4) == 25)
precondition(percentComplete(completed: 0, total: 0) == 0)""",
            observe="One of four complete is 25 percent, and an empty plan reports 0 instead of dividing by zero.",
            explain="The statistic uses only integers and a stated empty policy, so it needs no platform API and gives the same answer on Linux and Apple systems.",
        ),
        3: dict(
            explain="The Linux half was run: in a copy of JourneyCore on swift:6.3.3-noble, swift build ended with Build complete! and swift test reported Executed 4 tests, with 0 failures. The macOS half was not run for this reference; on a prepared Mac, follow the JourneyApp README and build JourneyMac with xcodebuild. Record the two results separately, since one does not prove the other.",
        ),
        4: dict(
            explain="UIKit exists only on Apple platforms, so a shared target that imports it stops compiling everywhere else. In the reference container, a one-line file with import UIKit failed with error: no such module 'UIKit'. Keep the domain target on Foundation or the standard library, and put UIKit code in the iOS app target or behind canImport(UIKit).",
        ),
        5: dict(
            code=r"""let capabilities: Set<String> = ["portable-core", "foundation-files"]
func runAction(_ capability: String) -> String {
  capabilities.contains(capability)
    ? "Running \(capability)" : "\(capability) is not available on this platform"
}
precondition(runAction("portable-core") == "Running portable-core")
precondition(runAction("swiftui-preview") == "swiftui-preview is not available on this platform")""",
            observe="A supported capability runs, and an unsupported one returns a sentence saying it is not available.",
            explain="Checking the declared capability set before acting turns a missing platform feature into a clear message rather than a crash or a Run button that does nothing.",
        ),
    },
    48: {
        1: dict(
            explain="In JourneyApp, tapping Save changes in ItemEditor calls store.update(id:title:completed:). PlanStore copies the plan into a candidate and calls StudyPlan.update, which finds the item by id and validates the new title. commit then writes the encoded candidate atomically and only afterward assigns plan, so @Observable publishes the change and PlanView redraws the row and the progress count.",
        ),
        2: dict(
            code=r"""let items = [
  CapstoneItem(id: "a", complete: true),
  CapstoneItem(id: "b", complete: false),
  CapstoneItem(id: "c", complete: true),
]
var progress: String { "\(items.filter(\.complete).count)/\(items.count) complete" }
precondition(progress == "2/3 complete")""",
            observe="Two of three items are complete, so the summary reads 2/3 complete.",
            explain="The count is computed from the items each time, so there is no second stored number that could drift out of sync after an edit.",
        ),
        3: dict(
            explain="The JourneyCore half was run: on swift:6.3.3-noble, swift build ended with Build complete!, swift test reported Executed 4 tests, with 0 failures, and swift run journey-demo printed JourneyCore: 1/2 complete; round trip passed. Running the full JourneyApp needs a prepared Apple destination and was not done for this reference; follow its README and record the destination you actually used.",
        ),
        4: dict(
            code=r"""enum CapstoneError: Error { case duplicate }
func buggyAdd(_ item: CapstoneItem, to items: [CapstoneItem]) -> [CapstoneItem] { items + [item] }
func add(_ item: CapstoneItem, to items: [CapstoneItem]) throws -> [CapstoneItem] {
  guard !items.contains(where: { $0.id == item.id }) else { throw CapstoneError.duplicate }
  return items + [item]
}
let start = [CapstoneItem(id: "a", complete: false)]
let broken = buggyAdd(CapstoneItem(id: "a", complete: true), to: start)
precondition(Set(broken.map(\.id)).count != broken.count)
precondition((try? add(CapstoneItem(id: "a", complete: true), to: start)) == nil)""",
            observe="The buggy add lets two items share id a, and the repaired add refuses the duplicate.",
            explain="Duplicate identity breaks lookup, navigation and saving, because one id now names two items. The repair checks identity before admitting a value, as StudyPlan.validate does.",
        ),
        5: dict(
            code=r"""struct StoredItem: Codable, Equatable {
  let id: String
  let title: String
}
func validated(_ items: [StoredItem]) -> Bool {
  Set(items.map(\.id)).count == items.count && items.allSatisfy { !$0.title.isEmpty }
}
precondition(validated([]))
let long = StoredItem(id: "l", title: String(repeating: "word ", count: 200))
precondition(validated([long]))
precondition(!validated([StoredItem(id: "x", title: "A"), StoredItem(id: "x", title: "B")]))
precondition((try? JSONDecoder().decode([StoredItem].self, from: Data("{".utf8))) == nil)
let saved = try JSONEncoder().encode([long])
let reloaded = try JSONDecoder().decode([StoredItem].self, from: saved)
precondition(reloaded == [long])""",
            observe="Empty and long-title plans are valid, duplicate ids fail, malformed storage does not decode, and a save then reload returns the same item.",
            explain="These portable checks cover the data rules. How long titles wrap and how the app reports malformed storage still have to be checked in JourneyApp itself.",
        ),
    },
}

for _number, _tasks in EXTRA.items():
    ANSWERS.setdefault(_number, {}).update(_tasks)
