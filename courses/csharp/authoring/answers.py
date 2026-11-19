"""Reference answers for guide tasks, executed inside the lesson reference.

Each entry maps a lesson number to {task number: answer}. An answer has `code` (a
block run after the worked examples, in the formatter's canonical style), `observe`
(the checked observation) and `explain` (why it works). Tasks without an entry are
reported as having no reference answer yet; `render.py` prints the coverage.
"""

ANSWERS = {
    1: {
        3: dict(
            code="""int rows = 4;
int seatsPerRow = 6;
int seats = rows * seatsPerRow;
Check(seats == 24, "four rows of six seats");""",
            observe="The program computes 24 seats and the check passes silently.",
            explain="Multiplication states the repeated rows directly, and the check compares the result with 24, a value written down independently of the formula.",
        )
    },
    2: {
        3: dict(
            code="""bool TryQuantity(string text, out int quantity) {
  var style = NumberStyles.None;
  var culture = CultureInfo.InvariantCulture;
  return int.TryParse(text, style, culture, out quantity);
}
Check(TryQuantity("42", out int count) && count == 42, "accepted");
Check(!TryQuantity("-1", out _), "negative rejected");
Check(!TryQuantity("4.5", out _), "fraction rejected");
Check(!TryQuantity("", out _), "empty rejected");""",
            observe="42 is accepted; -1, 4.5 and empty text are rejected without an exception.",
            explain="NumberStyles.None admits digits only, so a sign, a decimal point or whitespace makes TryParse return false. The caller receives a separate success flag instead of a sentinel quantity.",
        )
    },
    3: {
        3: dict(
            code="""decimal[] prices = { 19.99m, 5.01m, 0.35m };
decimal subtotal = prices.Sum();
decimal tax = subtotal * 0.0825m;
decimal payable = Math.Round(subtotal + tax, 2, MidpointRounding.ToEven);
Check(subtotal == 25.35m, "exact decimal subtotal");
Check(tax == 2.091375m, "unrounded tax");
Check(payable == 27.44m, "rounded only at the end");""",
            observe="Subtotal 25.35, unrounded tax 2.091375 and payable 27.44.",
            explain="decimal keeps the cents exact, the tax keeps its full precision, and only the final payable amount is rounded once with a named midpoint rule.",
        )
    },
    4: {
        3: dict(
            code="""bool SameKey(string left, string right) {
  return string.Equals(left, right, StringComparison.OrdinalIgnoreCase);
}
Check(SameKey("Report-ID", "report-id"), "case-insensitive match");
Check(!SameKey("report-id", "report_id"), "different characters differ");
Check(SameKey("i", "I"), "ordinal policy, no culture rules");""",
            observe="Keys that differ only by ASCII case match; a different separator does not.",
            explain="OrdinalIgnoreCase compares machine keys by code unit with simple case folding, so the result does not depend on the current culture.",
        )
    },
    5: {
        3: dict(
            code="""string Temperature(int celsius) {
  if (celsius < 0) {
    return "below zero";
  }
  if (celsius == 0) {
    return "zero";
  }
  return "above zero";
}
Check(Temperature(-5) == "below zero", "negative");
Check(Temperature(0) == "zero", "zero");
Check(Temperature(12) == "above zero", "positive");""",
            observe="-5, 0 and 12 are classified as below zero, zero and above zero.",
            explain="The three branches cover every int exactly once, and zero is tested on its own instead of being folded into either side.",
        )
    },
    6: {
        3: dict(
            code="""bool TryFirstIndex(int[] items, int target, out int index) {
  for (int i = 0; i < items.Length; i++) {
    if (items[i] == target) {
      index = i;
      return true;
    }
  }
  index = -1;
  return false;
}
var values = new[] { 5, 7, 7 };
Check(TryFirstIndex(values, 7, out int at) && at == 1, "first match");
Check(!TryFirstIndex(values, 9, out _), "not found");
Check(!TryFirstIndex(Array.Empty<int>(), 1, out _), "empty input");""",
            observe="The first 7 is at index 1; a missing target and an empty array both return false.",
            explain="The loop stops at the first match, and the Try pattern reports not-found through its bool result, so a caller checks that result before using the index instead of mistaking a sentinel such as -1 for a position.",
        )
    },
    7: {
        3: dict(
            code="""int Area(int width, int height) {
  if (width < 0 || height < 0) {
    throw new ArgumentOutOfRangeException(nameof(width));
  }
  return checked(width * height);
}
Check(Area(3, 4) == 12 && Area(0, 9) == 0, "valid dimensions");
bool rejected = false;
try {
  Area(-1, 2);
} catch (ArgumentOutOfRangeException) {
  rejected = true;
}
Check(rejected, "negative dimension rejected");""",
            observe="3 by 4 gives 12, a zero side gives 0, and a negative side throws.",
            explain="Validation happens before the calculation, and checked multiplication turns an overflow into an exception instead of a wrapped area.",
        )
    },
    8: {
        3: dict(
            code="""int[,] grid = { { 1, 2, 3 }, { 4, 5, 6 } };
int[] rowSums = new int[grid.GetLength(0)];
for (int row = 0; row < grid.GetLength(0); row++) {
  for (int col = 0; col < grid.GetLength(1); col++) {
    rowSums[row] += grid[row, col];
  }
}
Check(rowSums.SequenceEqual(new[] { 6, 15 }), "one sum per row");""",
            observe="The row sums are 6 and 15.",
            explain="The outer loop owns one result slot per row, and GetLength keeps both bounds tied to the actual rectangle.",
        )
    },
    9: {
        3: dict(
            code="""var original = new List<int> { -1, 2, -3, 4 };
List<int> positives = original.Where(value => value > 0).ToList();
Check(positives.SequenceEqual(new[] { 2, 4 }), "filtered copy");
Check(original.Count == 4 && original[0] == -1, "original unchanged");""",
            observe="The new list holds 2 and 4 while the original still has four items.",
            explain="Where reads the source and ToList builds a separate list, so no element of the original is removed.",
        )
    },
    10: {
        3: dict(
            code="""string[] tags = { "red", "blue", "red" };
var counts = new Dictionary<string, int>(StringComparer.Ordinal);
foreach (string tag in tags) {
  counts.TryGetValue(tag, out int before);
  counts[tag] = before + 1;
}
Check(counts["red"] == 2 && counts["blue"] == 1, "frequencies");
Check(counts.Count == 2, "one entry per distinct tag");""",
            observe="red counts 2 and blue counts 1.",
            explain="TryGetValue reads an absent tag as 0 before the increment, and the explicit ordinal comparer documents the identity policy.",
        )
    },
    11: {
        3: dict(
            code="""string Format(int? value) {
  if (value is null) {
    return "missing";
  }
  return value.Value == 0 ? "zero" : $"{value.Value} units";
}
Check(Format(null) == "missing", "missing stays missing");
Check(Format(0) == "zero", "zero is a measurement");
Check(Format(5) == "5 units", "positive measurement");""",
            observe="null, 0 and 5 are formatted as missing, zero and 5 units.",
            explain="The nullable parameter keeps absence separate from zero, and each of the three cases has its own text.",
        )
    },
    12: {
        3: dict(
            code="""var coordinate = new Point(1, 2);
var moved = coordinate;
moved.X = 5;
var session = new Counter();
var sameSession = session;
sameSession.Value = 3;
Check(coordinate.X == 1 && moved.X == 5, "coordinate copied by value");
Check(session.Value == 3, "session shared by reference");""",
            observe="Changing the copied coordinate leaves the original at 1, while both session variables see 3.",
            explain="A coordinate is a small value, so the Point struct copies it; a session is shared state with one identity, so the Counter class is shared by reference.",
        )
    },
    16: {
        3: dict(
            code="""var result = Import(new[] { "pear,2", "apple,3", "bad", "pear,1" });
var comparer = StringComparer.Ordinal;
var names = result.Counts.Keys.OrderBy(key => key, comparer);
var lines = new List<string>();
foreach (string name in names) {
  lines.Add($"{name}: {result.Counts[name]}");
}
lines.Add($"rejected: {result.Rejected}");
string report = string.Join("\\n", lines);
Check(report == "apple: 3\\npear: 3\\nrejected: 1", "sorted report");""",
            observe="The report lists apple: 3, pear: 3 and rejected: 1 in that order.",
            explain="Ordinal ordering makes the report deterministic, and the rejection count is reported beside the accepted totals instead of being hidden.",
        )
    },
    19: {
        3: dict(
            code="""int[] Transform(int[] values, Func<int, int> change) {
  var result = new int[values.Length];
  for (int i = 0; i < values.Length; i++) {
    result[i] = change(values[i]);
  }
  return result;
}
int[] input = { 1, 2, 3 };
int[] scaled = Transform(input, value => value * 10);
Check(scaled.SequenceEqual(new[] { 10, 20, 30 }), "delegate applied");
Check(input[0] == 1, "input unchanged");""",
            observe="Applying value * 10 gives 10, 20 and 30 and leaves the input unchanged.",
            explain="The caller supplies the behavior as a Func<int, int>, while the method owns iteration and the new result array.",
        )
    },
    20: {
        3: dict(
            code="""var stock = new Dictionary<string, int> { ["pear"] = 2, ["fig"] = 0 };
stock["apple"] = 5;
var kept = stock.Where(row => row.Value > 0);
var ordered = kept.OrderBy(row => row.Key, StringComparer.Ordinal);
var report = ordered.Select(row => $"{row.Key}={row.Value}");
Check(report.SequenceEqual(new[] { "apple=5", "pear=2" }), "report");""",
            observe="The report is apple=5 then pear=2; fig with quantity 0 is filtered out.",
            explain="Filtering, ordering with an explicit comparer and projecting happen in one query, and ToArray materializes the result once.",
        )
    },
    21: {
        3: dict(
            code="""var items = new[] { (Id: 1, Name: "pear"), (Id: 2, Name: "apple") };
var sales = new[] { (Id: 1, Qty: 2), (Id: 1, Qty: 3), (Id: 2, Qty: 4) };
var groups = sales.GroupBy(sale => sale.Id);
var totals = groups.ToDictionary(g => g.Key, g => g.Sum(s => s.Qty));
var report = items.Select(item => $"{item.Name}={totals[item.Id]}");
Check(report.SequenceEqual(new[] { "pear=5", "apple=4" }), "joined");""",
            observe="Each item appears once with its total: pear=5 and apple=4.",
            explain="Grouping first reduces sales to one row per item, so joining with the unique metadata cannot duplicate an item.",
        )
    },
    22: {
        3: dict(
            code="""IEnumerable<int> Cumulative(IEnumerable<int> values) {
  int total = 0;
  foreach (int value in values) {
    total = checked(total + value);
    yield return total;
  }
}
int[] totals = Cumulative(new[] { 1, 2, 3 }).ToArray();
Check(totals.SequenceEqual(new[] { 1, 3, 6 }), "running totals");
Check(!Cumulative(Array.Empty<int>()).Any(), "empty input");""",
            observe="1, 2, 3 produces 1, 3, 6; an empty input produces nothing.",
            explain="yield return makes the sequence lazy: each total is computed only when the consumer asks for the next element.",
        )
    },
    23: {
        3: dict(
            code="""int Import(string text, bool storageAvailable) {
  if (!int.TryParse(text, out int quantity) || quantity < 0) {
    throw new ArgumentException("invalid quantity", nameof(text));
  }
  if (!storageAvailable) {
    throw new IOException("storage unavailable");
  }
  return quantity;
}
Check(Import("3", true) == 3, "success");
string outcome = "none";
try {
  Import("x", true);
} catch (ArgumentException) {
  outcome = "invalid input";
}
Check(outcome == "invalid input", "input failure");
try {
  Import("3", false);
} catch (IOException) {
  outcome = "storage";
}
Check(outcome == "storage", "storage failure");""",
            observe="Valid input returns 3; bad text and unavailable storage end in different exception types.",
            explain="ArgumentException describes the caller's input and IOException the environment, so a caller can retry one and correct the other.",
        )
    },
    24: {
        3: dict(
            code="""string ReadAll(Stream stream) {
  var encoding = Encoding.UTF8;
  using var reader = new StreamReader(stream, encoding, leaveOpen: true);
  return reader.ReadToEnd();
}
using var source = new MemoryStream(Encoding.UTF8.GetBytes("data"));
Check(ReadAll(source) == "data", "content read");
Check(source.CanRead, "caller-owned stream stays open");""",
            observe="The helper returns data and the caller's stream is still readable afterward.",
            explain="leaveOpen: true makes the reader dispose only itself, so the stream's owner, the caller, decides when it closes.",
        )
    },
    25: {
        3: dict(
            code="""string name = "inventory-" + Guid.NewGuid().ToString("N");
string folder = Path.Combine(Path.GetTempPath(), name);
Directory.CreateDirectory(folder);
try {
  string path = Path.Combine(folder, "report.txt");
  string report = "pear: 3\\napple: 5";
  File.WriteAllText(path, report, Encoding.UTF8);
  Check(File.ReadAllText(path, Encoding.UTF8) == report, "round trip");
} finally {
  Directory.Delete(folder, true);
}
Check(!Directory.Exists(folder), "temporary folder removed");""",
            observe="The report reads back unchanged and the temporary folder is gone afterward.",
            explain="A unique folder under the temp path is owned by this code alone, and finally removes it whether or not the check passes.",
        )
    },
    26: {
        3: dict(
            code="""List<string> Decode(string json) {
  var errors = new List<string>();
  var item = JsonSerializer.Deserialize<ItemDto>(json);
  if (item is null || string.IsNullOrWhiteSpace(item.Name)) {
    errors.Add("name is required");
  }
  if (item is not null && item.Quantity < 0) {
    errors.Add("quantity must be nonnegative");
  }
  return errors;
}
string valid = "{\\"Name\\":\\"pear\\",\\"Quantity\\":2}";
Check(Decode(valid).Count == 0, "valid item");
Check(Decode("{\\"Quantity\\":-1}").Count == 2, "both errors reported");""",
            observe="A valid item gives no errors; a missing name with quantity -1 gives two errors.",
            explain="Decoding and validation are separate steps, and the decoder reports every problem it finds instead of stopping at the first.",
        )
    },
    27: {
        3: dict(
            code="""var start = new DateTimeOffset(2025, 3, 1, 22, 30, 0, TimeSpan.Zero);
var end = new DateTimeOffset(2025, 3, 2, 1, 15, 0, TimeSpan.Zero);
TimeSpan elapsed = end - start;
string report = $"{elapsed.TotalMinutes} minutes";
Check(elapsed == TimeSpan.FromMinutes(165), "across midnight");
Check(report == "165 minutes", "invariant report");""",
            observe="22:30 to 01:15 UTC is reported as 165 minutes.",
            explain="Fixed UTC instants make the duration independent of the machine's time zone, and subtraction handles the date change.",
        )
    },
    28: {
        3: dict(
            code="""bool ValidQuantity(int value) => value >= 0 && value <= 1000;
int[] inputs = { -1, 0, 1000, 1001 };
bool[] expected = { false, true, true, false };
for (int i = 0; i < inputs.Length; i++) {
  Check(ValidQuantity(inputs[i]) == expected[i], $"case {inputs[i]}");
}""",
            observe="All four rows pass, including both edges of the 0 to 1000 range.",
            explain="Each row pairs an input with an expected answer written independently, and the boundary rows make an off-by-one implementation fail.",
        )
    },
    29: {
        3: dict(
            code="""async Task<int> TotalAsync(IEnumerable<Task<int>> parts) {
  int[] values = await Task.WhenAll(parts);
  if (values.Any(value => value < 0)) {
    throw new ArgumentException("negative part");
  }
  return values.Sum();
}
var parts = new[] { Task.FromResult(2), Task.FromResult(5) };
Check(await TotalAsync(parts) == 7, "validated total");""",
            observe="Parts 2 and 5 produce the validated total 7.",
            explain="The method awaits every part before validating, so it never sums a partially known or negative input.",
        )
    },
    30: {
        3: dict(
            code="""var committed = new List<int>();
using var source = new CancellationTokenSource();
void Process(int[] items, CancellationToken token) {
  foreach (int item in items) {
    token.ThrowIfCancellationRequested();
    committed.Add(item);
    if (item == 2) {
      source.Cancel();
    }
  }
}
bool stopped = false;
try {
  Process(new[] { 1, 2, 3 }, source.Token);
} catch (OperationCanceledException) {
  stopped = true;
}
Check(stopped && committed.SequenceEqual(new[] { 1, 2 }), "kept work");""",
            observe="Processing stops before item 3, and items 1 and 2 remain committed.",
            explain="The loop checks the token before each item, so cancellation ends the work between items without undoing what was already committed.",
        )
    },
    31: {
        3: dict(
            code="""var channel = Channel.CreateBounded<int>(2);
Task producer = Task.Run(async () => {
  for (int i = 1; i <= 5; i++) {
    await channel.Writer.WriteAsync(i);
  }
  channel.Writer.Complete();
});
int sum = 0;
int count = 0;
await foreach (int value in channel.Reader.ReadAllAsync()) {
  sum += value;
  count++;
}
await producer;
Check(sum == 15 && count == 5, "every item consumed once");""",
            observe="The consumer receives five items, 1 to 5, and the sum is 15.",
            explain="WriteAsync waits while two items are buffered, and Complete tells the consumer that no more items will arrive, which ends the loop.",
        )
    },
    32: {
        3: dict(
            code="""string pear = "{\\"Name\\":\\"pear\\",\\"Quantity\\":2}";
string blank = "{\\"Name\\":\\"\\",\\"Quantity\\":1}";
string json = $"[{pear},{blank}]";
var items = JsonSerializer.Deserialize<ImportItem[]>(json)!;
var accepted = new Dictionary<string, int>(StringComparer.Ordinal);
int rejected = 0;
foreach (var item in items) {
  if (string.IsNullOrWhiteSpace(item.Name) || item.Quantity < 0) {
    rejected++;
    continue;
  }
  accepted.TryGetValue(item.Name, out int before);
  accepted[item.Name] = checked(before + item.Quantity);
}
Check(accepted["pear"] == 2 && accepted.Count == 1, "per-item result");
Check(rejected == 1, "rejection preserved");""",
            observe="pear has 2 accepted units and one rejected record is counted.",
            explain="Valid records update their own item total while invalid ones only increment the rejected count, so neither result hides the other.",
        )
    },
    33: {
        3: dict(
            code="""var gate = new Lock();
int left = 100;
int right = 0;
void Transfer(int amount) {
  lock (gate) {
    left -= amount;
    right += amount;
  }
}
Task Move() => Task.Run(() => Transfer(5));
var moves = new List<Task>();
for (int i = 0; i < 10; i++) {
  moves.Add(Move());
}
await Task.WhenAll(moves);
Check(left + right == 100 && right == 50, "sum preserved");""",
            observe="After ten concurrent transfers of 5 the balances are 50 and 50, still summing to 100.",
            explain="Both balances change inside one lock, so no other transfer can observe or interleave with a half-finished move.",
        )
    },
    34: {
        3: dict(
            code="""var counts = new ConcurrentDictionary<string, int>();
string[] words = { "a", "b", "a", "a" };
int Next(string key, int before) => before + 1;
Task Add(string w) => Task.Run(() => counts.AddOrUpdate(w, 1, Next));
await Task.WhenAll(words.Select(Add));
Check(counts["a"] == 3 && counts["b"] == 1, "concurrent frequencies");""",
            observe="a is counted 3 times and b once.",
            explain="AddOrUpdate may retry the update function under contention, so the function is pure: it computes the new count from the old one without side effects.",
        )
    },
    35: {
        3: dict(
            code="""int CountSeparators(ReadOnlySpan<char> text, char separator) {
  int count = 0;
  foreach (char ch in text) {
    if (ch == separator) {
      count++;
    }
  }
  return count;
}
Check(CountSeparators("a,b,c".AsSpan(), ',') == 2, "two separators");
Check(CountSeparators(ReadOnlySpan<char>.Empty, ',') == 0, "empty span");""",
            observe="a,b,c has two separators and an empty span has none.",
            explain="The helper is synchronous and only reads the span, so the borrowed text cannot escape the call.",
        )
    },
    36: {
        3: dict(
            code="""int SumPooled(int count) {
  int[] buffer = ArrayPool<int>.Shared.Rent(count);
  try {
    for (int i = 0; i < count; i++) {
      buffer[i] = i + 1;
    }
    return buffer.AsSpan(0, count).ToArray().Sum();
  } finally {
    ArrayPool<int>.Shared.Return(buffer, clearArray: true);
  }
}
Check(SumPooled(4) == 10, "logical range only");""",
            observe="Summing the first four slots gives 10.",
            explain="The rented array may be longer than requested, so the code uses only the first count slots, and finally returns the buffer on every path.",
        )
    },
    37: {
        3: dict(
            code="""string[] names = { "Pear", "apple", "Fig" };
string[] queries = { "PEAR", "fig", "kiwi" };
var policy = StringComparison.OrdinalIgnoreCase;
bool Scan(string q) => names.Any(n => string.Equals(n, q, policy));
int scanHits = queries.Count(Scan);
var index = new HashSet<string>(names, StringComparer.OrdinalIgnoreCase);
int indexHits = queries.Count(index.Contains);
Check(scanHits == 2 && indexHits == scanHits, "same answers");""",
            observe="Both approaches find 2 of the 3 queries.",
            explain="The index uses the same OrdinalIgnoreCase policy as the scan, so it answers identically while replacing a linear search per query with one hash lookup.",
        )
    },
    38: {
        3: dict(
            code="""var options = RegexOptions.NonBacktracking;
var limit = TimeSpan.FromSeconds(1);
var shape = new Regex(@"\\A[a-z][a-z0-9_]{0,15}\\z", options, limit);
var reserved = new HashSet<string>(StringComparer.Ordinal) { "admin" };
bool Valid(string id) => shape.IsMatch(id) && !reserved.Contains(id);
Check(Valid("report_2"), "accepted");
Check(!Valid("admin"), "reserved word rejected");
Check(!Valid("2report"), "shape rejected");""",
            observe="report_2 is accepted; admin and 2report are rejected for different reasons.",
            explain="The regular expression checks only the shape; the reserved-word rule is a separate domain check applied afterward.",
        )
    },
    39: {
        3: dict(
            code="""async Task<int> GetCountAsync(HttpClient client, CancellationToken ct) {
  var address = "https://example.invalid/count";
  using var response = await client.GetAsync(address, ct);
  response.EnsureSuccessStatusCode();
  string body = await response.Content.ReadAsStringAsync(ct);
  using var json = JsonDocument.Parse(body);
  return json.RootElement.GetProperty("count").GetInt32();
}
var handler = new FixtureHandler(HttpStatusCode.OK, "{\\"count\\":4}");
using var client = new HttpClient(handler);
Check(await GetCountAsync(client, CancellationToken.None) == 4, "count");""",
            observe="The method returns 4 from the fixture handler without any network access.",
            explain="The caller supplies both the HttpClient and the token, so tests can pass an offline handler and callers control cancellation.",
        )
    },
    40: {
        3: dict(
            code="""(int Total, int Rejected) Aggregate(IEnumerable<int> quantities) {
  int total = 0;
  int rejected = 0;
  foreach (int quantity in quantities) {
    if (quantity < 0) {
      rejected++;
    } else {
      total = checked(total + quantity);
    }
  }
  return (total, rejected);
}
var result = Aggregate(new[] { 2, -1, 3 });
Check(result.Total == 5 && result.Rejected == 1, "core aggregation");""",
            observe="Quantities 2, -1 and 3 aggregate to total 5 with one rejection.",
            explain="The core takes plain values and returns plain values; it knows nothing about files, HTTP or the console, so any adapter can call it.",
        )
    },
    42: {
        3: dict(
            code="""string[] allowed = { "line", "field", "reason" };
var safe = new HashSet<string>(allowed, StringComparer.Ordinal);
var error = new Dictionary<string, string>();
error["line"] = "4";
error["field"] = "quantity";
error["reason"] = "negative";
error["token"] = "synthetic-secret";
var visible = error.Where(item => safe.Contains(item.Key));
var shown = visible.ToDictionary(item => item.Key, item => item.Value);
Check(shown.Count == 3 && !shown.ContainsKey("token"), "allowlisted");""",
            observe="The visible error keeps line, field and reason and drops the token.",
            explain="An allowlist names what may be shown, so a new sensitive field is hidden by default instead of leaking until someone adds it to a blocklist.",
        )
    },
    44: {
        3: dict(
            code="""int[] quantities = { 3, -1, 4, -2, 5 };
int submitted = quantities.Length;
int accepted = quantities.Count(quantity => quantity >= 0);
int rejected = quantities.Count(quantity => quantity < 0);
Check(submitted == 5 && accepted == 3 && rejected == 2, "counts");
Check(accepted + rejected == submitted, "every record accounted for");""",
            observe="5 submitted records split into 3 accepted and 2 rejected.",
            explain="All three counts come from the same input, so the accounting check would fail if a record were dropped or counted twice.",
        )
    },
    45: {
        3: dict(
            code="""var metrics = new[] { new Metric(2), new Metric(5) };
Func<Metric, int> count = metric => metric.Count;
int total = metrics.Sum(count);
Check(total == 7, "typed projection");""",
            observe="The typed projection sums the counts to 7.",
            explain="A Func<Metric, int> is checked by the compiler; renaming Count breaks the build instead of a reflection lookup failing at run time.",
        )
    },
    47: {
        3: dict(
            code="""var receipts = new Dictionary<string, int>(StringComparer.Ordinal);
int executions = 0;
int Execute(string id, int amount) {
  if (receipts.TryGetValue(id, out int receipt)) {
    return receipt;
  }
  executions++;
  receipts[id] = amount * 10;
  return receipts[id];
}
int first = Execute("op-1", 3);
int retry = Execute("op-1", 3);
Check(first == 30 && retry == 30, "same receipt");
Check(executions == 1, "command ran once");""",
            observe="Both calls return receipt 30, and the command ran only once.",
            explain="The lookup answers a repeated request from the stored receipt, so a retry after an unknown outcome cannot apply the command a second time.",
        )
    },
}
