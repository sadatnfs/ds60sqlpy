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

# Per-task reasoning. A written answer has `explain` (the approach), `why`, `wrong` (one
# plausible wrong approach and why it fails here) and `verify`. For a task that already
# has executed `code`, only `wrong` and `verify` are added; its code and observation stay.
REASONING = {
    5: {
        1: dict(
            explain='With `label` null, `label != null` is false, so `&&` returns false without evaluating `label.Length > 0`, and the outer `!` turns that into true for the `guarded access` check. After `label = "ok"` both operands run: the null test is true and `Length == 2` is true.',
            why="C# evaluates the right operand of `x && y` only when `x` is true. The dereference therefore sits behind a precondition that has already been proved, and the null case never reaches `.Length`.",
            wrong="Distributing the negation by hand as `!(label != null) && label.Length > 0` looks equivalent but is not. When `label` is null the left side is true, so `label.Length` runs and throws `NullReferenceException`, which is the exact access the original parentheses prevent.",
            verify='Replace the right operand with a helper such as `bool Longer(string s) { Console.WriteLine("read Length"); return s.Length > 0; }`. With the null label nothing is printed; with `"ok"` the line appears once, and both checks stay silent before the lesson marker.',
        ),
        2: dict(
            explain='Change only the retry arm to `< 70 => "retry"` and move the boundary checks with it: `Classify(69) == "retry"`, `Classify(70) == "pass"`, and keep `Classify(101) == "invalid"`. Arm order stays `< 0`, `< 70`, `<= 100`, `_`.',
            why="A switch expression takes the first arm whose pattern matches. 69 matches `< 70` first, while 70 fails it and lands in `<= 100`, so 70 is the inclusive pass boundary and the invalid categories at both ends are untouched.",
            wrong='Writing `<= 70 => "retry"` moves the boundary one value too far: `Classify(70)` returns `retry` and the at-boundary check throws. Updating only the checks to 69 and 70 while leaving `< 60` fails the other way, because 69 then passes.',
            verify="A failing `Check` throws `InvalidOperationException` carrying its reason, so an off-by-one version stops at `at boundary`. The corrected classifier lets all three checks pass silently and the run ends with `csharp-005: passed`.",
        ),
        3: dict(
            wrong='A two-way ternary `celsius <= 0 ? "below zero" : "above zero"` folds zero into the negative side. `Temperature(0)` then returns `below zero` and the `zero` check throws, which is why zero has its own branch.',
            verify="The `Task 3` block checks -5, 0 and 12. Extra probes at `int.MinValue` and `int.MaxValue` should return `below zero` and `above zero`, showing the three branches cover the whole `int` range.",
        ),
        4: dict(
            explain="For `bool` operands `&` is the non-conditional logical AND: it evaluates both sides before combining them. In `label != null & label.Length > 0` with a null label, `label.Length` still runs and throws `NullReferenceException`, so the guard guards nothing.",
            why="Only `&&` and `||` are conditional operators. `&` and `|` always evaluate both operands, which is useful when the right side has a required effect but wrong when it depends on the left side being true.",
            wrong="Treating it as a precedence problem and writing `(label != null) & (label.Length > 0)` changes nothing. The parentheses already matched the intent; the defect is evaluation order, and only restoring `&&` fixes it.",
            verify="Run the `&` version with `label = null`: execution stops with `NullReferenceException` before the `guarded access` check reports anything. Restore `&&` and the same fixture passes silently.",
        ),
        5: dict(
            explain='The valid domain is 0 through 100. Check `Classify(-1) == "invalid"`, `Classify(0) == "retry"`, `Classify(100) == "pass"` and `Classify(101) == "invalid"`: one value on each side of each edge.',
            why="The arms `< 0` and `<= 100` define both edges. These four inputs are the smallest set that separates an inclusive edge from an exclusive one at each end, which a middle score such as 75 cannot do.",
            wrong='Testing only 50 and 101 passes a classifier that says `< 100 => "pass"`, where 100 falls through to `invalid`, and one that rejects 0 with `<= 0 => "invalid"`. Both wrong edges survive because neither test touches them.',
            verify="Mutate `<= 100` to `< 100` temporarily; the `Classify(100)` check must throw. Mutate `< 0` to `<= 0`; the `Classify(0)` check must throw. Restore both and all four pass.",
        ),
        6: dict(
            explain="Route a ticket priority of 1, 2 or 3 to an `enum Route { Page, Queue, Backlog }` with `priority switch { 1 => Route.Page, 2 => Route.Queue, 3 => Route.Backlog, _ => throw new ArgumentOutOfRangeException(nameof(priority)) }`. Invalid input is a rejection, not a fourth route.",
            why="The three constant patterns are disjoint, so each valid priority matches exactly one arm. Keeping invalid values out of the enum means no caller can confuse a rejected ticket with a low-priority one. A limitation is that callers must handle the exception, or the policy must return a separate result type instead.",
            wrong="Using `_ => Route.Backlog` as the fallback is compact but sends priority 0 or 7 to the backlog as if it were valid. That is the lesson's pitfall of an else branch classifying every invalid value as valid.",
            verify="Check 1, 2 and 3 map to `Page`, `Queue` and `Backlog`, then call it with 0 and 4 inside `try` blocks and `Check` that `ArgumentOutOfRangeException` was caught each time.",
        ),
    },
    8: {
        1: dict(
            explain="`alias` and `source` hold the same array reference, so `alias[0] = 9` writes into the one shared array and `source` becomes `{ 9, 4 }`. `copy` was cloned before the write into separate storage, so `copy[0]` is still 2.",
            why="Arrays are reference types: assignment copies the reference, not the elements. `Clone` allocates a new `int[]` and copies each element, and `int` elements are values, so nothing is shared after the clone.",
            wrong="Predicting that `copy` also changes because `Clone` is shallow misreads the pitfall. Shallowness only matters when elements are references; for `int[]` the shallow copy already duplicates every value.",
            verify='Keep the `alias versus copy` check and add `Check(ReferenceEquals(alias, source) && !ReferenceEquals(copy, source), "identity")`. Both pass silently.',
        ),
        2: dict(
            explain="After Example A, write `copy[1] = 7;` and check `source[1] == 4 && copy[1] == 7`. Only the cloned array receives the write.",
            why="The clone owns its own two slots, so a write through `copy` cannot reach the storage that `source` and `alias` share.",
            wrong="Making the copy with `int[] copy = source;` instead of `Clone` creates a second alias. The write to `copy[1]` then changes `source[1]` to 7 and the new check throws.",
            verify="Run the corrected version and the check passes. Temporarily replace `(int[])source.Clone()` with plain assignment and confirm the same check now fails; that proves the check can tell a copy from an alias.",
        ),
        3: dict(
            wrong="Using `grid.Length` as the row bound treats the 6 cells as 6 rows. The loop reaches `grid[2, 0]` and throws `IndexOutOfRangeException`, and `new int[grid.Length]` would also allocate six result slots for two rows.",
            verify="The block checks `rowSums` against `{ 6, 15 }`. Their total, 21, must also match Example B's `all six cells` sum, a cross-check that every cell was counted once.",
        ),
        4: dict(
            explain="The defect reads `col < grid.GetLength(0)` in the inner loop. On the 2 by 3 grid it visits only columns 0 and 1, so the sum is 1 + 2 + 4 + 5 = 12 instead of 21. The fix is `col < grid.GetLength(1)`.",
            why="`GetLength(0)` is the row count and `GetLength(1)` the column count. Each loop bound must come from the dimension that its index variable addresses.",
            wrong="Testing the fix on a 3 by 3 grid proves nothing, because the buggy and correct bounds are both 3. Replacing the bound with `grid.Length` is also wrong: 6 overruns the column index and throws.",
            verify="With the bug, the `all six cells` check throws because the sum is 12. On a 3 by 2 grid the same bug throws `IndexOutOfRangeException` at column 2 instead. After the fix the sum is 21 and the check is silent.",
        ),
        5: dict(
            explain="Check `int[] empty = Array.Empty<int>();` has `Length == 0` and that a summing loop over it returns 0. For `int[,] oneRow = { { 7, 8, 9 } };` check `GetLength(0) == 1`, `GetLength(1) == 3` and a row sum of 24.",
            why="A loop bounded by `Length` or `GetLength` simply does not execute for size 0, and a single row keeps its own column count, so both shapes need no special branch.",
            wrong="Reading `empty[0]` as a default first value throws `IndexOutOfRangeException`. For the single row, using `oneRow.Length` as the row count gives 3 rows instead of 1 and overruns `oneRow[1, 0]`.",
            verify="All checks pass silently. Add `new int[0, 3]` as a third case: `GetLength(1)` is 3 while `Length` is 0, which shows shape and cell count are different facts.",
        ),
        6: dict(
            explain="Use jagged storage, `double[][] histories`, with one inner array per sensor, for example 3 readings for sensor 0 and 5 for sensor 1. Each row's own `Length` is its history length.",
            why="A rectangular `double[,]` forces one column count on every row, so shorter histories would need padding. Jagged rows record each real length directly. The limitation is that inner arrays can be null and there is no single `GetLength(1)`, so code must check each row.",
            wrong="A `new double[sensors, 5]` array padded with zeros looks tidy, but sensor 0's mean is then computed over 5 slots, two of them fake zeros, and is understated. Padding with `NaN` instead silently poisons the sum.",
            verify="Check `histories[0].Length == 3 && histories[1].Length == 5`, and compute each mean by dividing by that row's own `Length`; compare with a hand calculation for both sensors.",
        ),
    },
    9: {
        1: dict(
            explain="`new List<int>(10)` starts with `Count == 0` and `Capacity >= 10`. After `Add(3)` and `Add(5)`, `Count` is 2 and `Capacity` is unchanged, because two entries fit in the reserved buffer.",
            why="`Count` is the number of logical entries; `Capacity` is the size of the internal array. The buffer grows only when an `Add` would exceed it, and the exact growth rule is an implementation detail.",
            wrong="Treating capacity as valid positions and reading `values[5]` fails: the indexer checks against `Count`, so it throws `ArgumentOutOfRangeException` even though the buffer has room.",
            verify='After the appends add `Check(values.Capacity >= 10, "buffer kept")`, and wrap `_ = values[5];` in a `try` block that must catch `ArgumentOutOfRangeException`.',
        ),
        2: dict(
            explain="After the two appends, write `values[1] = 8;`. The list becomes `{ 3, 8 }` and `Count` remains 2.",
            why="The indexer setter overwrites a slot that already exists in the range 0 to `Count - 1`; it never adds a slot, so the count cannot change.",
            wrong="`values.Insert(1, 8)` looks like a replacement but shifts 5 to the right, giving `{ 3, 8, 5 }` with `Count` 3. Using `values[2] = 8` to append throws `ArgumentOutOfRangeException` because index 2 equals `Count`.",
            verify="Check `values.Count == 2 && values.SequenceEqual(new[] { 3, 8 })`; it passes silently.",
        ),
        3: dict(
            wrong="Dropping `.ToList()` keeps `positives` as a deferred `Where` query over `original`. Nothing is copied: if `original.Add(6)` runs later, the next enumeration of `positives` yields 2, 4 and 6. Calling `original.RemoveAll(value => value <= 0)` instead mutates the source, and the `original unchanged` check throws.",
            verify="After building `positives`, add `original.Add(6)` and check `positives.Count == 2`. The materialized list passes; the deferred query version would report 3.",
        ),
        4: dict(
            explain='`foreach (int v in values) if (v < 0) values.Remove(v);` removes -1 and then the next `MoveNext` throws `InvalidOperationException` with "Collection was modified". Repair it with `values.RemoveAll(v => v < 0)`, or iterate a snapshot `values.ToArray()` while removing from `values`.',
            why="`List<T>` keeps a version number that every structural change increments, and its enumerator compares versions on each step. `RemoveAll` owns traversal and removal together, so no outside enumerator is invalidated.",
            wrong="A forward `for` loop with `RemoveAt(i)` avoids the exception but skips the element after each removal. It happens to work on `{ -1, 2, -3, 4 }` because the negatives are not adjacent, yet on `{ -1, -2, 3 }` it leaves `{ -2, 3 }`.",
            verify="Catch `InvalidOperationException` around the original loop and `Check` it was raised. Then check that the repaired code turns `{ -1, -2, 3 }` into `{ 3 }`; that adjacent-negatives fixture exposes the forward-index bug.",
        ),
        5: dict(
            explain="Run `RemoveAll(v => v < 0)` on three fixtures: `{ 1, 2 }` returns 0 and leaves both, `{ -1, -2 }` returns 2 and leaves `Count` 0, and an empty list returns 0 and stays empty.",
            why="`RemoveAll` returns how many entries it removed and handles any size, including zero, so asserting both the return value and the remaining sequence pins the behavior at each extreme.",
            wrong="Looping `values.Remove(values.Find(v => v < 0))` breaks on the no-removal case: `Find` returns `default(int)`, which is 0, when nothing matches. On `{ 0, 1 }` that removes a legitimate 0.",
            verify="Check the returned counts 0, 2 and 0 and compare each list with `SequenceEqual`. Add `{ 0, 1 }` as a fourth fixture and confirm it is unchanged.",
        ),
        6: dict(
            explain='Treat each edit as producing a new list and push the previous list onto a `Stack<List<string>>`: `history.Push(current); current = new List<string>(current) { "b" };`. Undo is `current = history.Pop();`.',
            why="Views holding the old reference keep the version they rendered, and undo restores state by reassignment instead of reversing each mutation. The cost is copying every line on each edit, and if lines were mutable objects the copy would still share them.",
            wrong="Mutating `current` in place and pushing the same reference onto the stack stores an alias, not a history. Undo then pops a list that already contains the edit, so nothing is undone.",
            verify='Start from `{ "a" }`, apply the edit, check `current` is `{ "a", "b" }`, undo, and check it is `{ "a" }` again. The aliasing version fails the second check.',
        ),
    },
    10: {
        1: dict(
            explain='`TryGetValue("OAK", out int zero)` returns true with 0, because the `OrdinalIgnoreCase` comparer matches the stored `Oak`. `TryGetValue("Pine", out _)` returns false and its out value is also 0. Only the Boolean result separates them.',
            why="`TryGetValue` reports presence through its return value and sets the out parameter to `default` when the key is absent, so the integer by itself cannot carry absence.",
            wrong='Comparing `counts.GetValueOrDefault("Pine")` with 0 treats a missing tree as a counted tree with zero sightings. Indexing `counts["Pine"]` instead throws `KeyNotFoundException`.',
            verify='Add `Check(counts.ContainsKey("OAK") && !counts.ContainsKey("Pine"), "presence")` and `Check(counts.GetValueOrDefault("Pine") == counts["Oak"], "same zero")`; both pass, showing the value alone hides the difference.',
        ),
        2: dict(
            explain='Construct the dictionary with `StringComparer.Ordinal`. The lookup for `OAK` now returns false, so look up `Oak` for the present zero and add `Check(!counts.TryGetValue("OAK", out _), "case matters")`.',
            why="The comparer supplies both hashing and equality for keys. Ordinal comparison matches exact UTF-16 code units, so `OAK` and `Oak` are different keys under it.",
            wrong='Normalizing only the lookup with `"oak".ToUpper()` still searches for `OAK` while the stored key is `Oak`. The entry looks lost, although the dictionary is behaving exactly as the ordinal comparer specifies.',
            verify="Run with both checks: the present zero is found under `Oak`, `OAK` is absent, and `counts.Count` is still 1.",
        ),
        3: dict(
            wrong="`counts[tag]++` without a prior entry throws `KeyNotFoundException` on the first `red`, because the indexer getter runs before the increment. Calling `counts.Add(tag, 1)` for every tag throws `ArgumentException` on the second `red`.",
            verify='The block checks red 2, blue 1 and two entries. Append `"Red"` to `tags`: under `StringComparer.Ordinal` the count becomes 3 entries, which confirms the stated identity policy.',
        ),
        4: dict(
            explain='`int n = counts["Pine"];` throws `KeyNotFoundException` because the indexer getter requires the key to exist. Choose a policy: `TryGetValue` when absence is expected, `GetValueOrDefault` only when a missing tag truly means a count of 0, or let the exception stand when absence means corrupted input.',
            why="Each policy states what absence means instead of relying on whatever the indexer happens to do. `TryGetValue` costs one lookup and keeps presence and value separate.",
            wrong="Wrapping the indexer in `try { n = counts[key]; } catch { n = 0; }` makes absence look like a zero count, and the bare `catch` also swallows unrelated failures such as the `ArgumentNullException` a null key raises.",
            verify="Catch `KeyNotFoundException` from the unguarded indexer and `Check` it occurred, then check that the `TryGetValue` version returns false for `Pine` with no exception.",
        ),
        5: dict(
            explain='Feed the frequency loop three fixtures: an empty array gives `counts.Count == 0`; `{ "red", "red", "red" }` gives `red` 3 with one entry; `{ "red", "Red" }` gives two entries under `Ordinal` and one entry with count 2 under `OrdinalIgnoreCase`.',
            why="The loop creates an entry only on a key's first sighting, and the comparer alone decides whether `red` and `Red` are that same key.",
            wrong='Expecting the case variants to merge regardless of comparer makes `counts["red"] == 2` fail under `Ordinal`. Under `OrdinalIgnoreCase`, expecting the stored key to read `Red` is also wrong: the dictionary keeps the first spelling, `red`.',
            verify='Check each count and `counts.Keys.Single() == "red"` for the case-insensitive fixture; all checks pass silently.',
        ),
        6: dict(
            explain="Give each customer an immutable surrogate key, such as a `Guid Id` assigned at creation, and store records in `Dictionary<Guid, Customer>`. Fields such as `Email` and `DisplayName` may change without touching the key.",
            why="A hash table places an entry by the key's hash at insertion. If the key never changes, the bucket stays correct for the record's lifetime. The limitation is that the id must exist before insertion and must never be reused.",
            wrong='Putting the records themselves in a `HashSet<Customer>`, where `record Customer(Guid Id, string Email)` compares every property, breaks on an email change: `customer with { Email = "new@x.test" }` is a different value and `set.Contains(updated)` is false.',
            verify="Insert a customer, update its email with `with`, and check `byId.ContainsKey(updated.Id)` is true while `set.Contains(updated)` is false.",
        ),
    },
    11: {
        1: dict(
            explain='For `string? label = null`, `label?.Length` short-circuits to `null`, so `length` is an absent `int?` and `length ?? -1` yields -1. For `label = ""` the access runs and `length` is a present 0, so `length ?? -1` is 0, not -1.',
            why="`?.` lifts the result to `int?` and produces null only when the receiver is null. An empty string is a real object with `Length` 0, so the fallback operator `??` has nothing to replace and passes the 0 through.",
            wrong="Predicting -1 for both inputs treats empty text as missing. That merges two states the lesson keeps apart: a caller reading -1 could not tell an absent label from one that exists but has no characters.",
            verify='Add `string? empty = ""; int? emptyLength = empty?.Length;` and check `emptyLength == 0 && (emptyLength ?? -1) == 0` next to the existing `absence remains absent` check. All of them pass silently.',
        ),
        2: dict(
            explain='Replace the sentinel with a label at the display boundary: `string shown = length is int n ? n.ToString() : "unknown";`. For the null label `shown` is `unknown`; for `"ok"` it is `2`.',
            why="The pattern `length is int n` succeeds only for a present value and binds a nonnullable `n`. The missing case gets a word that cannot be mistaken for a length, unlike -1, which a later sum or average would happily include.",
            wrong="Formatting with `(length ?? 0).ToString()` produces `0` for the missing label. A report then shows zero characters for text that never existed, the early fallback the pitfalls warn against.",
            verify='Check `shown == "unknown"` for the null label and `shown == "2"` after assigning `"ok"`. Then feed an empty string and confirm it shows `0`, not `unknown`.',
        ),
        3: dict(
            wrong="Declaring the parameter as plain `int` and having callers pass `value ?? 0` collapses missing into zero before `Format` runs. `Format(null)` then cannot even be written, and the data that reaches the method prints `zero` for a missing reading.",
            verify="The block checks null, 0 and 5. Also probe `Format(-3)`: it returns `-3 units`, which shows the formatter treats negative readings as measurements; decide whether the domain should reject them instead.",
        ),
        4: dict(
            explain="`string? name = null; int size = name!.Length;` compiles without warning because `!` tells the flow analysis to trust you, but at run time the dereference still throws `NullReferenceException`. Fix it with a real branch: `int size = name is null ? 0 : name.Length;` or reject the input.",
            why="Nullable annotations and the `!` operator exist only at compile time. They change which warnings appear and emit no runtime check, so the generated code is the same dereference as without the operator.",
            wrong="Moving the suppression earlier, as in `string checkedName = name!;`, silences the same warning one line sooner. The null now travels further into the program and fails at a later `.Length`, farther from its cause.",
            verify='Run the `!` version with `name = null` and observe `NullReferenceException`. With the branch, check `size == 0` for null and `size == 3` for `"Ada"`; both pass.',
        ),
        5: dict(
            explain='Classify text with `string Kind(string? s) => s is null ? "null" : s.Length == 0 ? "empty" : string.IsNullOrWhiteSpace(s) ? "blank" : "text";` and check null, `""`, `"   "` and `"a"` separately.',
            why='Each test isolates one state. `"   "` has `Length` 3, so it passes an emptiness test, yet `IsNullOrWhiteSpace` reports true. Ordering null, then empty, then whitespace keeps every arm reachable.',
            wrong='Using `string.IsNullOrEmpty(s)` as the only guard lets `"   "` through as valid text. A required-name field would then accept three spaces as a real name.',
            verify='Check `Kind(null) == "null"`, `Kind("") == "empty"`, `Kind("   ") == "blank"` and `Kind("a") == "text"`. Also add a tab, `"\\t"`, and confirm it is `blank`.',
        ),
        6: dict(
            explain="For a discount field in an import, use `decimal? Discount` where a missing column means no discount data was supplied, `0` means the supplier explicitly offers none, and an empty cell is rejected as malformed. Parse each case into its own outcome before computing prices.",
            why="Keeping three outcomes stops a missing field from silently pricing an item at full rate. The limitation is that downstream reports must handle `null`, for example by showing `unknown` and excluding it from averages.",
            wrong="Parsing every blank or missing cell with `decimal.TryParse(cell, out var d) ? d : 0` makes an absent discount indistinguishable from an explicit zero, so audits cannot find suppliers who never sent the field.",
            verify="Feed three rows: one without the column, one with `0` and one with an empty cell. Check the results are `null`, `0m` and a rejection, then confirm an average over the rows uses only the explicit zero.",
        ),
    },
    13: {
        1: dict(
            explain="`new Wallet(10)` starts at 10. `TrySpend(4)` passes both guards, subtracts and returns true, leaving 6. `TrySpend(7)` hits `amount > Balance` because 7 is greater than 6, returns false before subtraction, and the balance stays 6.",
            why="The method runs its checks in order: malformed input throws, unaffordable input returns false, and only an accepted amount reaches `Balance -= amount`. A rejected call therefore exits before any state change.",
            wrong="Assuming `TrySpend(7)` takes the balance to -1 and then reports false misreads the order of statements. That would be the subtract-first defect from task 4, not the code shown.",
            verify="After the second call, check `wallet.Balance == 6` and then `wallet.TrySpend(6) && wallet.Balance == 0`. The `rejection retains balance` check and the new one both pass silently.",
        ),
        2: dict(
            explain="Add `public void Deposit(int amount) { if (amount <= 0) throw new ArgumentOutOfRangeException(nameof(amount)); Balance += amount; }`. Check that depositing 5 into a wallet of 10 gives 15 and that `Deposit(-2)` throws with the balance still 15.",
            why="The guard runs before the only mutation, so a malformed amount cannot lower the balance. Using the private setter keeps every change to `Balance` inside methods that validate first.",
            wrong="Validating with `if (Balance + amount < 0)` accepts `Deposit(-3)` on a balance of 10, turning a deposit into a hidden withdrawal of 3 that bypasses `TrySpend` entirely.",
            verify="Catch `ArgumentOutOfRangeException` around `Deposit(-2)` and check both that it was caught and that `Balance` is unchanged. Decide and test whether `Deposit(0)` is allowed; this answer rejects it.",
        ),
        3: dict(
            explain="Write `sealed class Inventory { public int Stock { get; private set; } public Inventory(int stock) { if (stock < 0) throw new ArgumentOutOfRangeException(nameof(stock)); Stock = stock; } public bool TryReserve(int quantity) { if (quantity <= 0) throw new ArgumentOutOfRangeException(nameof(quantity)); if (quantity > Stock) return false; Stock -= quantity; return true; } }`.",
            why="The constructor establishes `Stock >= 0`, and `TryReserve` subtracts only after proving `quantity <= Stock`, so the result can never go negative. The private setter prevents callers from bypassing the check.",
            wrong="A public `Stock` property with a separate `Reserve` method lets a caller write `inventory.Stock -= 5` directly, so the invariant depends on every caller remembering the rule rather than on the class.",
            verify="With stock 3, check `TryReserve(2)` leaves 1, `TryReserve(2)` returns false with 1 left, and `TryReserve(1)` leaves 0. Wrap `TryReserve(0)` and `new Inventory(-1)` in `try` blocks expecting `ArgumentOutOfRangeException`.",
        ),
        4: dict(
            explain="The defect is `Balance -= amount; if (Balance < 0) return false;`. With a balance of 6, `TrySpend(7)` sets `Balance` to -1 before returning false, so the rejected call has already corrupted the state. Move the comparison before the subtraction.",
            why="Failure atomicity requires the check to precede the mutation. Once the field has changed, returning false only reports the problem; it does not undo it.",
            wrong="Patching it with `Balance -= amount; if (Balance < 0) { Balance += amount; return false; }` restores the value but briefly publishes -1. Any exception or concurrent reader between the two statements sees the broken invariant.",
            verify="Run Example A against the buggy method: `!wallet.TrySpend(7) && wallet.Balance == 6` throws because the balance is -1. With the check moved first, it passes.",
        ),
        5: dict(
            explain="With a wallet of 5, check `TrySpend(5)` returns true and leaves 0, `TrySpend(0)` returns true and leaves the balance unchanged, and `TrySpend(-1)` throws `ArgumentOutOfRangeException` with the balance unchanged.",
            why="`amount > Balance` is false when they are equal, so spending exactly the available amount is accepted. Zero passes both guards as a no-op, and a negative value is caught by the first guard before any change.",
            wrong="Writing the affordability test as `amount >= Balance` rejects spending the full balance, so `TrySpend(5)` on a balance of 5 returns false. A test that only used 3 and 7 would never notice.",
            verify="Run the three cases in order on fresh wallets and check each return value and the final `Balance`. Then temporarily change `>` to `>=` and confirm the exact-amount check throws.",
        ),
        6: dict(
            explain="Yes. `TrySpend` reads `Balance`, compares and then writes, so two tasks can both read 10, both find 7 affordable, and both subtract, leaving -4. Protect the read, compare and write with one `lock` on a private object.",
            why="The invariant holds only if the check and the mutation happen as one step. A lock serializes callers so the second task sees the balance after the first spend. The cost is contention; a single-threaded wallet does not need it.",
            wrong="Marking `Balance` as `volatile` or reading it with `Interlocked.Read` makes each individual read fresh but does not join the read and the write, so the same double spend still occurs.",
            verify="Start 100 tasks that each call `TrySpend(1)` on a wallet of 50 and count the true results. With the lock, exactly 50 succeed and the balance is 0; without it, repeated runs can produce a negative balance.",
        ),
    },
    14: {
        1: dict(
            explain='`first == second` is true because the record compares `Name` and `Age`, both `"Ada"` and 30. `ReferenceEquals(first, second)` is false because two `new` expressions created two objects.',
            why="A record class synthesizes `Equals`, `==` and `GetHashCode` over its declared members, while `ReferenceEquals` always compares object identity and cannot be overridden.",
            wrong="Assuming `==` on a reference type always means identity predicts false here. That holds for ordinary classes but not for records, whose synthesized operator compares data.",
            verify='Add `var third = first; Check(ReferenceEquals(first, third) && first == third, "same object");` beside the two Example A checks and confirm all three pass.',
        ),
        2: dict(
            explain='Write `var renamed = first with { Name = "Grace" };` and check `first.Name == "Ada"`, `renamed.Name == "Grace"`, `renamed.Age == 30` and `renamed != first`.',
            why="`with` calls the record copy constructor and then sets only the listed members, so `Age` carries over and the original object is not touched.",
            wrong='Trying `first.Name = "Grace"` fails to compile, because positional record properties are `init`-only. Declaring a mutable `Name { get; set; }` to make it compile would change the original in place and lose the earlier value.',
            verify='Run the four checks; all pass silently. Also check `(renamed with { Name = "Ada" }) == first` to show equality is decided by data, not by how the instance was produced.',
        ),
        3: dict(
            explain="Declare `public readonly record struct Point(int X, int Y);`. Use `var a = new Point(1, 2); var b = a with { X = 5 };` and check `a.X == 1`, `b.X == 5`, `b.Y == 2` and `new Point(1, 2) == a`.",
            why="A record struct is a value type, so assignment copies the data, and `readonly` makes the generated properties `init`-only. No alias can change a stored point.",
            wrong="A plain `record struct Point(int X, int Y)` without `readonly` gets settable properties, so `a.X = 9` compiles and the coordinate is no longer immutable even though it is still compared by value.",
            verify="Check the four results, then add `a.X = 9;` and confirm the compiler rejects it because `X` is init-only. Remove that line and check `var c = a; c = c with { Y = 7 };` leaves `a.Y == 2`, since each struct variable holds its own copy.",
        ),
        4: dict(
            explain="`record Entry(string Label, List<int> Values)` looks immutable, but `entry.Values.Add(4)` changes the list that every copy made with `with` also holds. Store `IReadOnlyList<int>` built from `values.ToArray()` or an `ImmutableList<int>` in the constructor.",
            why="The positional properties are `init`-only, which protects the reference, not the object it points to. Copying the input into a new read-only collection breaks the link to the caller's list.",
            wrong="Changing only the property type to `IReadOnlyList<int>` while storing the caller's `List<int>` still shares it. The caller can keep adding to the original list and the history entry changes with it.",
            verify='Build `var source = new List<int> { 1, 2 }; var entry = new Entry("a", source); source.Add(3);` and check `entry.Values.Count == 2` and `!ReferenceEquals(entry.Values, source)`. Without the copy the count is 3 and the first check throws.',
        ),
        5: dict(
            explain="Build `var a = new Basket(new List<int> { 1, 2 }); var b = new Basket(new List<int> { 1, 2 });`. `a == b` is false even though the lists hold the same numbers; `a.Items.SequenceEqual(b.Items)` is true.",
            why="The synthesized equality calls `EqualityComparer<List<int>>.Default`, which for `List<int>` is reference equality. Two distinct lists are unequal regardless of contents.",
            wrong="Expecting `a == b` to be true because records have value equality assumes the comparison is recursive. It compares each member with that member type's own equality, and `List<T>` does not override it.",
            verify="Check `!(a == b)` and `a.Items.SequenceEqual(b.Items)`. Then make `b` with `a with { }` and check `a == b` is true because both now hold the same list reference.",
        ),
        6: dict(
            explain="Give an order identity-based equality on a stable `OrderId`, not on all of its data. Its status and lines change after creation, and a `HashSet<Order>` keyed on every field would lose track of an order once it was updated.",
            why="Hash-based collections place an item using the hash at insertion. If the hash comes from mutable data, updating the order moves its correct bucket and `Contains` returns false. A fixed ID keeps the hash stable. The cost is that two orders with identical contents are still different orders.",
            wrong='Declaring `record Order(int OrderId, string Status)` and replacing it with `order with { Status = "Shipped" }` creates a new value that is unequal to the stored one, so the set now holds the stale order and `Contains(updated)` is false.',
            verify="Insert an order into a `HashSet`, produce the shipped version, and check `Contains`. With equality on `OrderId` only, it is true; with full record equality, it is false.",
        ),
    },
    15: {
        1: dict(
            explain='For `Describe(0)` the first arm needs `number > 0`, so it falls to `int => "nonpositive"`. `Describe(12)` matches the first arm, `positive`. `Describe("")` reaches `string { Length: 0 }`, `empty`. `Describe("hi")` matches no specific arm and gets `other`.',
            why="Arms are tried top to bottom, and an arm matches only when its type pattern and any property pattern or `when` guard all succeed. A failed guard moves evaluation to the next arm instead of stopping.",
            wrong='Predicting an exception for `"hi"` because no string arm covers it ignores the `_` discard, which matches every remaining value. Predicting `positive` for 0 forgets that the guard is strictly greater than zero.',
            verify='Add checks for `Describe(0) == "nonpositive"` and `Describe("hi") == "other"` to the two Example A checks; all pass.',
        ),
        2: dict(
            explain='Insert `string { Length: > 0 } => "text"` after the `string { Length: 0 }` arm and before `_`. Check `Describe("") == "empty"` and `Describe("hi") == "text"`.',
            why="The new property pattern matches only strings with at least one character, so it does not overlap the empty arm, and placing it before the discard keeps the discard for non-string values such as `3.5`.",
            wrong='Adding a bare `string => "text"` above the empty arm matches every string first, so `""` returns `text`. The compiler reports the empty arm as unreachable (CS8510), which is exactly the shadowing to avoid.',
            verify='Check `""`, `"hi"` and `3.5` give `empty`, `text` and `other`. Swap the two string arms temporarily and confirm the build fails with the unreachable-arm error.',
        ),
        3: dict(
            explain='Declare `abstract record Op; sealed record Loading : Op; sealed record Ready(string Data) : Op; sealed record Failed(string Error) : Op;` and render with `op switch { Loading => "loading", Ready(var d) => $"ready:{d}", Failed(var e) => $"failed:{e}", _ => throw new InvalidOperationException("unknown state") }`.',
            why="Each state carries only its own payload, so a loading operation cannot have data and a ready one cannot have an error. Positional deconstruction gives each arm a nonnullable value to use.",
            wrong="A single `record Op(bool Loading, string? Data, string? Error)` allows `Loading = true` with `Data` set, or both `Data` and `Error` null when not loading. Every consumer must then guess which field wins.",
            verify='Check `new Loading()` renders `loading`, `new Ready("rows")` renders `ready:rows` and `new Failed("timeout")` renders `failed:timeout`.',
        ),
        4: dict(
            explain='In `item switch { object => "other", int number when number > 0 => "positive", ... }` the first arm matches every non-null value, so later arms never run. Move `object` (or `_`) to the end.',
            why="Switch expressions choose the first matching arm. Since every type converts to `object`, that arm subsumes the rest, and the compiler reports the later arms as unreachable with error CS8510.",
            wrong="Keeping the broad arm first and adding `when item is not int` to it hides the error but duplicates the type tests by hand. Each new specific arm then needs another exclusion in the guard.",
            verify='Compile the broken order and observe CS8510 on the `int` arm. After moving `object` last, `Describe(12) == "positive"` passes.',
        ),
        5: dict(
            explain='Add `sealed record Pending : Result;` without updating `Render`. `Render(new Pending())` reaches `_ => throw new InvalidOperationException("unknown result")`, and a test should expect exactly that exception.',
            why="The C# compiler does not know that `Result` has only `Success` and `Failure`, because any code may derive another subclass. Throwing on the discard makes a forgotten case loud rather than silently rendered as success.",
            wrong='Making the fallback `_ => "count:0"` keeps the program running but reports a pending result as success with zero items, the pitfall of a default branch hiding a new state.',
            verify="Wrap `Render(new Pending())` in `try` and catch `InvalidOperationException`, checking its `Message` is `unknown result`. Success and failure still render as before.",
        ),
        6: dict(
            explain="Replace `bool isConnected, isConnecting; string? error;` with records `Disconnected`, `Connecting(int Attempt)`, `Connected(string Session)` and `Lost(string Error)`. The flag combination `isConnected && isConnecting` and an `error` while connected can no longer be expressed.",
            why="With three independent flags there are 8 combinations, of which only 4 are meaningful. Four exclusive records describe exactly the meaningful ones, so code cannot build the other 4. The limitation is that a new state forces every switch to be reviewed.",
            wrong="Keeping the flags and adding an enum `ConnectionState` alongside them leaves two sources of truth. A bug can set the enum to `Connected` while `error` is still set.",
            verify="Write a `Describe` switch over the four records and check one value of each, such as `new Connecting(2)` giving `connecting:2`. `Connected` takes only a session string, so a connected state carrying an error cannot be written at all.",
        ),
    },
    17: {
        1: dict(
            explain="`IRate rate = new FlatRate(3)` stores a `FlatRate` behind an `IRate` variable. `rate.Cost(4)` is an interface call, so the runtime dispatches to `FlatRate.Cost`, which computes `checked(3 * 4)` and returns 12. `Total(rate, 0)` makes the same call with 0 units and gets 0.",
            why="The static type `IRate` decides which members can be called, while the object created by `new` decides which method body runs. `Total` never names `FlatRate`, yet it reaches that implementation through the interface slot.",
            wrong="Expecting `Total` to need a `FlatRate` overload, or a cast such as `((FlatRate)rate).Cost(4)`, misses the point of the contract. The cast compiles but throws `InvalidCastException` as soon as Example B passes a `CappedRate`.",
            verify='Add `Check(rate.GetType() == typeof(FlatRate), "runtime type");` next to the `flat rate` check. Both pass, and swapping in `new CappedRate(3, 10)` changes the result of `rate.Cost(4)` to 10 without editing `Total`.',
        ),
        2: dict(
            explain="Create `IRate premium = new FlatRate(5);` and check `Total(premium, 4) == 20` beside `Total(new FlatRate(3), 4) == 12`. `Total` keeps its one-line body.",
            why="`FlatRate` is a positional record, so each instance carries its own `Price`. `Total` reads the price only through `Cost`, so a second rate needs no change in the consumer.",
            wrong="Adding a `price` parameter to `Total` and computing `price * units` inside it bypasses the interface. The capped policy then disappears, because `Total(capped, 4)` would ignore `Cap` and return 12 instead of 10.",
            verify="Run both checks plus the existing `capped policy` check; all pass. `git diff` on the `Total` line should show no change.",
        ),
        3: dict(
            explain='Declare `public interface ILabelFormatter { string Format(string name, int count); }` and implement `public sealed record PlainLabel : ILabelFormatter { public string Format(string name, int count) => $"{name}:{count}"; }`. The contract states that equal inputs always produce the same text.',
            why="One method with explicit inputs keeps the interface small, and a deterministic implementation can be tested by comparing strings. Nothing in the contract depends on time, culture or random state.",
            wrong='An implementation using `$"{name}:{count:N0}"` looks harmless but formats 1234 as `1,234` or `1.234` depending on `CultureInfo.CurrentCulture`, so the same inputs give different labels on different machines.',
            verify='Check `new PlainLabel().Format("pear", 3) == "pear:3"` and that two calls with the same arguments return equal strings. Add `Format("pear", 1234) == "pear:1234"`; the `N0` variant fails it wherever the culture inserts a group separator.',
        ),
        4: dict(
            explain="A `CentsRate(300)` whose `Cost(4)` returns 1200 has the right signature but breaks the contract that results are whole currency units. `Total` passes 1200 on as if it were 1200 units of currency, a hundredfold overcharge. Convert inside the implementation or reject it.",
            why="The compiler checks only that `Cost` takes and returns `int`. Units are part of the behavior callers rely on, so two implementations that disagree on units are not substitutable even though both compile.",
            wrong="Dividing by 100 inside `Total` fixes the cents implementation but breaks `FlatRate`: `Total(new FlatRate(3), 4)` becomes 0 because integer division truncates 12 / 100.",
            verify="Run the same consumer test against both implementations: `Total(rate, 4)` must be 12 for a price of 3 whole units. The cents version fails with 1200, and after the fix both return 12.",
        ),
        5: dict(
            explain="For `CappedRate(3, 10)`, check `Total(rate, 0) == 0`. The cap is reached when `3 * units == 10`, which has no integer solution, so test the nearest values: 3 units cost 9 (below the cap) and 4 units cost 10 (capped). Use `CappedRate(5, 10)` to hit the cap exactly with 2 units.",
            why="`Math.Min(Price * units, Cap)` returns the product when it is at or below the cap and the cap above it. Testing 9, exactly 10 and 12 before capping shows both branches and the equality case.",
            wrong="Capping the unit count instead of the cost, as in `Price * Math.Min(units, Cap / Price)`, looks equivalent but `Cap / Price` truncates 10 / 3 to 3, so `CappedRate(3, 10).Cost(4)` returns 9 and undercharges by 1. Only a test at or just past the cap shows it.",
            verify="Check `new CappedRate(5, 10).Cost(2) == 10`, `new CappedRate(3, 10).Cost(3) == 9` and `Total(new CappedRate(3, 10), 0) == 0`. All pass silently.",
        ),
        6: dict(
            explain="Inject the source of inventory rows, for example `interface IRowSource { IEnumerable<string> ReadRows(); }`, instead of letting the importer call `File.ReadAllLines` itself. Production passes a file-backed source; tests pass an in-memory list.",
            why="The importer's parsing and validation rules can then be tested with exact rows, including malformed ones, without creating files or depending on paths. The limitation is one more type to maintain and wire up at startup.",
            wrong="Injecting an interface for the importer's own private parsing helper adds indirection without a testing benefit, because tests already reach that helper through the public import call. The pitfall is an interface that exposes implementation detail.",
            verify='Write a test with an in-memory source containing `"pear,2"` and `"bad"`. Check that one item is imported and one row is reported as rejected, without touching the file system.',
        ),
    },
    18: {
        1: dict(
            explain='`Max(4, 9)` infers `T` as `int` from both arguments and returns `int` 9. `Max("apple", "pear")` infers `string` and returns `"pear"`. `Max(5, 5)` is again `int`.',
            why="Type inference looks at the argument types. Both arguments must agree on one `T`, and that `T` must satisfy `IComparable<T>`, which both `int` and `string` do.",
            wrong="Predicting that the result is typed as the constraint, `IComparable<int>`, leads to unnecessary casts such as `(int)Max(4, 9)`. The return type is `T` itself, so `Max(4, 9) + 1` compiles directly and is 10.",
            verify='Add `int next = Max(4, 9) + 1; Check(next == 10, "typed result");`. Also check `Max(4, 9.5) == 9.5`: the `int` argument converts to `double`, so inference picks `double` for that call.',
        ),
        2: dict(
            explain="Call `decimal price = Max(19.99m, 5.25m);` and check `price == 19.99m`. Both literals carry the `m` suffix, so `T` is `decimal`.",
            why="`decimal` implements `IComparable<decimal>`, so it satisfies the constraint and the method returns a `decimal` without any conversion or boxing.",
            wrong="Writing `Max(19.99, 5.25m)` mixes a `double` literal with a `decimal`, which fails inference. Casting both to `double` to make it compile loses decimal precision for money values.",
            verify="Check `Max(19.99m, 5.25m) == 19.99m` and `Max(0.1m + 0.2m, 0.3m) == 0.3m`; with `decimal` the sum is exactly 0.3, so the tie returns the left value and the check passes.",
        ),
        3: dict(
            explain="Declare `public record Triple<T>(T First, T Second, T Third) { public Triple<T> Rotate() => new(Second, Third, First); }`. Check `new Triple<int>(1, 2, 3).Rotate() == new Triple<int>(2, 3, 1)`.",
            why="The single type parameter states that all three positions hold the same type, and the positional record gives `init`-only properties and value equality, so the container is immutable and comparable.",
            wrong="Using `record Triple(object First, object Second, object Third)` compiles, but `First` comes back as `object`, so reading it as an `int` needs a cast that can throw `InvalidCastException`, the object escape the pitfalls warn about.",
            verify='Check the rotation, then check `new Triple<string>("a", "b", "c").First == "a"` with no cast. Try `triple.First = 9;` and confirm the compiler rejects the init-only property.',
        ),
        4: dict(
            explain="In `int Size<T>(T value) => value.Length;` the compiler reports CS1061 because `T` could be `int`, which has no `Length`. Inside the method only members of `object` are known.",
            why="A generic method is compiled once for every possible `T`, so it may only use operations every allowed type supports. Without a constraint, that set is just `object`'s members.",
            wrong="Adding `where T : class` does not help, because a class constraint promises a reference type, not a `Length` property. Casting through `dynamic` compiles but fails at run time with `RuntimeBinderException` when `T` is `int`.",
            verify="Compile the unconstrained version and read CS1061. Rewrite it as `int Size<T>(IReadOnlyCollection<T> value) => value.Count;`, which asks for exactly the capability it uses, and check `Size(new[] { 1, 2, 3 }) == 3`.",
        ),
        5: dict(
            explain='`Max` returns `left` when `CompareTo` is greater than or equal to 0, so ties return the first argument. Use records with equal ordering but different identity: `record Item(int Rank, string Name) : IComparable<Item>` comparing only `Rank`, then `Max(new Item(1, "a"), new Item(1, "b")).Name == "a"`.',
            why="With integers, the first and second tie values are indistinguishable, so a test cannot see which one was returned. Objects that compare equal but carry different names make the tie policy observable.",
            wrong="Testing only `Max(5, 5) == 5` passes whether the method returns `left` or `right`. Changing `>= 0` to `> 0` would silently switch the policy to the second argument and that check would still pass.",
            verify='Check the `Item` tie returns `"a"`. Temporarily change `>= 0` to `> 0` and confirm the check now throws because `"b"` is returned.',
        ),
        6: dict(
            explain="Write `static T FirstOr<T>(IEnumerable<T> items, Func<T, bool> keep, T fallback)` with no constraint at all, because it only enumerates and calls a delegate. Contrast with `Max`, which needs `IComparable<T>` because it calls `CompareTo`.",
            why="Each constraint narrows which types callers may use. A helper that never compares or constructs `T` should accept every type, including structs and nullable references.",
            wrong="Adding `where T : IComparable<T>` to `FirstOr` by habit compiles but blocks a caller with a list of records that are not comparable, for no algorithmic reason.",
            verify="Call `FirstOr(new[] { 1, 4, 6 }, n => n > 3, 0)` and expect 4, then call it with a list of an uncomparable `record Tag(string Name)` and confirm it compiles and returns the first match.",
        ),
    },
    20: {
        1: dict(
            explain="In Example A the query is created over `{ 1, 2 }`, 3 is added, and enumeration later yields 2 and 3. In Example B `ToArray()` runs while the list is still `{ 1, 2 }`, so the snapshot holds only 2 and adding 3 afterward does not reach it.",
            why="`Where` returns an object that remembers the source and predicate but reads no elements. `ToArray` enumerates immediately and copies the matches into a new array, which later list changes cannot alter.",
            wrong="Expecting Example A's query to contain only 2 treats `Where` as eager filtering. That would be true for `values.Where(...).ToList()`, but this query has not run when 3 is added.",
            verify="Check `query.Count() == 1` before `values.Add(3)` and `query.Count() == 2` after it. The same query object reports two counts at two moments, while an array from `ToArray()` taken before the add keeps `Length == 1`.",
        ),
        2: dict(
            explain='Write `var labels = values.Select(value => $"item-{value}");` and check `labels.SequenceEqual(new[] { "item-1", "item-2", "item-3" })` after the three values exist.',
            why="`Select` maps each element through the lambda in order, producing one string per integer without filtering, so the output length equals the input length.",
            wrong='Putting the projection in `Where`, as in `values.Where(value => $"item-{value}" != "")`, compiles but still yields integers, because `Where` keeps elements and never transforms them.',
            verify='Check the sequence of labels, then add 4 to `values` and check `labels.Last() == "item-4"`, showing the projection is also deferred.',
        ),
        3: dict(
            explain="Filtering, ordering with `StringComparer.Ordinal` and projecting are composed as one deferred query; nothing runs until `SequenceEqual` enumerates `report`. Add `.ToArray()` at the end when a stable snapshot is needed.",
            wrong='Ordering by `row.Key` without a comparer uses the current culture. That gives the same result for `apple` and `pear`, but with a key `"Banana"` a linguistic culture puts `apple` first while ordinal order puts `Banana` first, so the report can differ between machines.',
            verify='The `report` check expects `apple=5` then `pear=2`. Set `stock["fig"] = 1` just before the check and it throws, because the deferred query now yields `apple=5`, `fig=1`, `pear=2`. The report is computed when enumerated, not when built.',
        ),
        4: dict(
            explain="With `int calls = 0; var query = values.Select(v => { calls++; return v * 2; });`, calling `query.Count()` and then `query.Sum()` runs the lambda twice per element, so `calls` is 6 for three values, not 3. Materialize once with `var doubled = query.ToArray();` and use `doubled` twice.",
            why="A deferred query is a recipe. Each enumeration runs the whole pipeline again from the source, including any side effects in the lambdas.",
            wrong="Caching with `var cached = query;` copies only the reference to the same recipe. Calling `cached.Count()` and `cached.Sum()` still runs the lambda twice per element and `calls` is still 6.",
            verify="Check `calls == 6` after the two calls on `query`, then reset it, use `ToArray()` once and check `calls == 3` after both `doubled.Length` and `doubled.Sum()`.",
        ),
        5: dict(
            explain="Check `Array.Empty<int>().Where(v => v > 1).ToArray().Length == 0` and that `new[] { 1 }.Where(v => v > 1)` has no elements. Also check `Sum()` returns 0 on both and `First()` throws `InvalidOperationException`.",
            why="An empty source and a filter that matches nothing both produce an empty sequence. Aggregates such as `Sum` define 0 for empty input, while `First` has no element to return and throws.",
            wrong="Using `query.First()` to read the top row in a report assumes at least one match. With the filter matching nothing it throws `Sequence contains no elements`; `FirstOrDefault()` returns 0 instead, which must not be confused with a real value.",
            verify="Run the empty checks and wrap `First()` in `try` catching `InvalidOperationException`. Check `FirstOrDefault()` returns 0 and decide whether 0 is a valid data value in your report.",
        ),
        6: dict(
            explain="For a large import, stream rows with `File.ReadLines(path).Select(Parse).Where(IsValid)` and consume them once with `foreach`, writing each accepted row as it arrives. Materialize only a small summary such as counts.",
            why="Streaming keeps memory proportional to one row instead of the whole file. The tradeoff is repeatability: enumerating the query again rereads and reparses the file, and the file may have changed in between.",
            wrong="Calling `File.ReadAllLines(path)` and then `.ToList()` on the parsed rows makes two full in-memory copies of a large file. Leaving the query deferred and calling `Count()` before the import loop reads the whole file twice.",
            verify="Count calls to `Parse` with a counter: one streaming pass over a 1,000-row test file should increment it exactly 1,000 times. Calling `Count()` first should show 2,000.",
        ),
    },
    22: {
        1: dict(
            explain="`RangeFrom(5, 4).Take(2)` pulls two values. The iterator yields 5, then 6, and `Take` stops asking after the second, so 7 and 8 are never computed. `RangeFrom(5, 0).Any()` calls `MoveNext` once and gets false.",
            why="Each `MoveNext` call resumes the iterator until the next `yield return`. `Take(2)` stops calling `MoveNext` after two items, and `SequenceEqual` then disposes the enumerator.",
            wrong="Assuming the loop computes all four values up front and `Take` trims the result describes an array-returning method. With `yield return`, the remaining iterations never run at all.",
            verify="Add a counter inside the loop, for example a static `produced` incremented before each `yield return`. After `RangeFrom(5, 4).Take(2).ToArray()` it is 2, not 4.",
        ),
        2: dict(
            explain="Add `static IEnumerable<int> EverySecond(int start, int count) { if (count < 0) throw new ArgumentOutOfRangeException(nameof(count)); return Iterate(); IEnumerable<int> Iterate() { for (int i = 0; i < count; i++) yield return checked(start + 2 * i); } }` and check `EverySecond(0, 3)` is `{ 0, 2, 4 }`.",
            why="Following the `RangeFrom` pattern, validation happens before the iterator is returned, and the loop is bounded by `count`, so the sequence is finite and each step adds 2.",
            wrong="Writing `while (true) yield return start += 2;` with no count gives an infinite sequence. `EverySecond(0).ToArray()` then never returns, and `start += 2` also skips the starting value.",
            verify="Check `EverySecond(0, 3).SequenceEqual(new[] { 0, 2, 4 })`, `EverySecond(7, 2).SequenceEqual(new[] { 7, 9 })` and `!EverySecond(7, 0).Any()`, and confirm `EverySecond(0, -1)` throws at the call.",
        ),
        3: dict(
            wrong="Materializing inside the method with `var list = new List<int>(); ... return list;` gives the same totals but computes all of them before returning, so `Cumulative(hugeSource).First()` would read the entire input first.",
            verify="The block checks `1, 3, 6` and empty input. Also check `Cumulative(new[] { int.MaxValue, 1 }).First() == int.MaxValue` succeeds while `.ToArray()` throws `OverflowException` at the second element, showing the overflow is raised lazily.",
        ),
        4: dict(
            explain="If `count < 0` is checked inside a method that itself contains `yield return`, `var seq = Broken(0, -1);` returns without error. The `ArgumentOutOfRangeException` appears only at the first `MoveNext`, perhaps far from the faulty call. Split the method as `RangeFrom` does.",
            why="The compiler turns a method containing `yield` into a state machine, and none of its body, including the guard, runs until enumeration begins. A non-iterator outer method runs immediately.",
            wrong="Adding `.ToList()` at the call site, as in `Broken(0, -1).ToList()`, surfaces the exception immediately, but only for callers that remember it. A caller that stores the sequence for later still gets the late failure, and the eager copy gives up laziness.",
            verify="With the broken version, the Example B `try` block catches nothing and `rejected` stays false, so the check throws. With the split version the same block sets `rejected` to true.",
        ),
        5: dict(
            explain="Check `!RangeFrom(3, 0).Any()`, `RangeFrom(3, 1).SequenceEqual(new[] { 3 })` and that `RangeFrom(3, -1)` throws `ArgumentOutOfRangeException` when called, before any enumeration.",
            why="A count of 0 never enters the loop, a count of 1 yields exactly `start`, and the outer guard rejects a negative count. Those three inputs cover the loop bound and the guard.",
            wrong="Writing the bound as `i <= count` yields one extra value: `RangeFrom(3, 0)` produces 3 instead of nothing and `RangeFrom(3, 1)` produces 3 and 4, so both count checks throw.",
            verify="Run the three checks. Then change `<` to `<=` temporarily and confirm the empty-range check throws.",
        ),
        6: dict(
            explain="Expose `IEnumerable<string> ReadRecords(string path)` built with `File.ReadLines`, and document that each enumeration reopens and rereads the file, that the file is closed when a `foreach` finishes or breaks, and that callers wanting a snapshot must call `ToList`.",
            why="`File.ReadLines` opens the file when called and closes it when the enumerator is disposed, which `foreach` does even after `break`. A second enumeration opens the file again. Memory stays at one line at a time.",
            wrong="Returning the enumerator directly and having callers call `MoveNext` by hand risks skipping `Dispose`, which keeps the file handle open until finalization, so a later write to the file fails with `IOException`.",
            verify="Enumerate `ReadRecords(path).Take(1)` in a `foreach`, then open the same file for writing with `FileShare.None`; it succeeds because the reader was disposed.",
        ),
    },
    24: {
        1: dict(
            explain="In Example A, `Dispose` runs at the closing brace of `using (resource) { ... }`, after the `open inside scope` check and before `closed after scope`. In Example B the `throw` leaves the block, `Dispose` runs on the way out, and only then does control reach the empty `catch`.",
            why="The compiler expands `using (x) { body }` into `try { body } finally { x?.Dispose(); }`. A `finally` runs whether the block finishes normally or by an exception, so both examples dispose at the same boundary.",
            wrong="Predicting that Example B skips cleanup because the exception jumps straight to `catch` ignores the hidden `finally`. Expecting the garbage collector to close the probe later is also wrong: `Probe` has no finalizer, and nothing else sets `Closed`.",
            verify='Change Example B to `catch (InvalidOperationException) { Check(resource.Closed, "disposed before catch"); }`. It passes, proving `Dispose` ran before the handler.',
        ),
        2: dict(
            explain='Add `sealed class Named(string name, List<string> log) : IDisposable { public void Dispose() => log.Add(name); }`, then write `using (var outer = new Named("outer", log)) using (var inner = new Named("inner", log)) { }` and check `log.SequenceEqual(new[] { "inner", "outer" })`.',
            why="Nested `using` statements become nested `try`/`finally` blocks, and the inner `finally` runs first. The same reverse order applies to `using var` declarations at the end of their scope.",
            wrong="Expecting declaration order, `outer` then `inner`, would be harmful for real wrappers. If `outer` were a `FileStream` and `inner` a `StreamWriter`, disposing the stream first would make the writer's final flush throw `ObjectDisposedException`.",
            verify="Run the check, then rewrite with two `using var` lines in a block and confirm the log is still `inner`, `outer`.",
        ),
        3: dict(
            wrong="Writing `using var reader = new StreamReader(stream, encoding);` without `leaveOpen: true` makes disposing the reader also dispose `source`. `source.CanRead` becomes false and the `caller-owned stream stays open` check throws.",
            verify='After the block, set `source.Position = 0;` and check `ReadAll(source) == "data"` a second time. A closed stream would throw `ObjectDisposedException` on the position change.',
        ),
        4: dict(
            explain="`Stream Open() { using var s = new MemoryStream(bytes); return s; }` hands back a stream that was disposed as the method returned, so the caller's `ReadByte()` throws `ObjectDisposedException`. Return the stream without `using` and document that the caller owns it and must dispose it.",
            why="A `using var` disposes at the end of its enclosing scope, which here is the method body. `return` does not cancel the `finally`, so ownership must move to the caller explicitly.",
            wrong="Removing the `using` without telling callers to dispose leaks the resource instead. With a `FileStream` the handle stays open until finalization, so a later `File.Open` with `FileShare.None` on the same path fails with `IOException`.",
            verify='With the bug, `Check(Open().CanRead, "usable")` throws. After the fix, `using var s = Open(); Check(s.CanRead && s.ReadByte() >= 0, "usable");` passes.',
        ),
        5: dict(
            explain='Write `void Work(Probe p, bool fail, ref bool finished) { using (p) { if (fail) throw new InvalidOperationException("fixture"); finished = true; } }`. With `fail = true`, catch the exception and check `p.Closed && !finished`; with `fail = false`, check `p.Closed && finished`.',
            why="The two flags separate cleanup from completion. Cleanup must be true on both paths, while completion is true only on the normal one, so the test proves the exception really happened before the work finished.",
            wrong="Calling `p.Dispose()` as the last statement of the block instead of using `using` passes the normal-path test. On the failure path the throw skips that line, so `Closed` stays false; testing only `fail = false` would never show it.",
            verify="Run both cases. Then replace `using (p)` with a trailing `p.Dispose();` and confirm the `fail = true` check throws.",
        ),
        6: dict(
            explain="Document: `RowParser(Stream stream, bool leaveOpen = false)` always owns its internal `StreamReader`, and owns the stream only when `leaveOpen` is false. `Dispose` disposes the reader, which closes the stream unless `leaveOpen` is true.",
            why="This mirrors `StreamReader`'s own convention, so a caller can predict who closes what. A caller that reads a header with one parser and the body with another passes `leaveOpen: true` to the first.",
            wrong="A parser whose `Dispose` always closes the stream breaks that two-parser pattern: the second parser's first read throws `ObjectDisposedException` because the caller's stream was released by someone that only borrowed it.",
            verify="Over a `MemoryStream`, dispose a parser created with `leaveOpen: true` and check `stream.CanRead` is true; repeat with `false` and check it is false.",
        ),
    },
    27: {
        1: dict(
            explain="`a` is 12:00 at +02:00, which is 10:00 UTC, and `b` is 10:00 at UTC. `==` on `DateTimeOffset` compares the UTC instants, so they are equal, while `Offset` is 2 hours for `a` and 0 for `b`.",
            why="A `DateTimeOffset` stores a local clock reading and its offset from UTC. Equality and ordering use `UtcDateTime`; the offset is kept only for display. `EqualsExact` is the method that also compares offsets.",
            wrong="Comparing `a.DateTime == b.DateTime` or `a.Hour == b.Hour` compares the wall-clock parts 12:00 and 10:00 and reports a two-hour difference between what is one instant.",
            verify='Add `Check(a.UtcDateTime == b.UtcDateTime, "same UTC");` and `Check(!a.EqualsExact(b), "offsets differ");`. Both pass beside the existing checks.',
        ),
        2: dict(
            explain="Parse `a` as `2025-01-01T12:01:00+02:00`. Now `a == b` is false, `a > b` is true and `a - b` is exactly one minute.",
            why="Subtraction and comparison convert both values to UTC first: 10:01 against 10:00.",
            wrong="Subtracting the wall-clock readings, 12:01 minus 10:00, predicts 121 minutes. That number is real only for two timestamps in the same offset, and these differ by two hours.",
            verify="Check `a - b == TimeSpan.FromMinutes(1)` and `a > b`; then change `b` to `10:01:00Z` and check that `a == b` is true again.",
        ),
        3: dict(
            wrong='The interpolation `$"{elapsed.TotalMinutes} minutes"` formats a `double` with the current culture. 165 has no fractional part, but a 90.5-minute interval prints `90,5 minutes` under a culture such as `de-DE`, so machine-read reports should use `elapsed.TotalMinutes.ToString(CultureInfo.InvariantCulture)`.',
            verify="The block checks 165 minutes and the report text. Add `Check(elapsed.TotalHours == 2.75)` and check that `start - end` is `-165` minutes, which shows the sign follows the order of subtraction.",
        ),
        4: dict(
            explain="A stored `2025-01-10T09:00+01:00` for a Paris meeting fixes the offset, not the zone. `AddMonths(6)` keeps +01:00 and yields 09:00 at +01:00 in July, but Paris is then at +02:00, so the meeting shows as 10:00 local. Store the zone ID `Europe/Paris` and convert with `TimeZoneInfo`.",
            why="An offset records how one moment relates to UTC. A time zone is a set of rules, including daylight-saving changes, that gives a different offset on different dates.",
            wrong="Storing only UTC and calling `ToLocalTime()` for display swaps one mistake for another: the result now depends on the zone of the machine running the code, so a server in UTC shows 08:00 for a 09:00 Paris meeting.",
            verify='On a machine with time zone data, check `TimeZoneInfo.FindSystemTimeZoneById("Europe/Paris").GetUtcOffset(new DateTime(2025, 7, 10))` is 2 hours while the January date gives 1 hour.',
        ),
        5: dict(
            explain='Write `TimeSpan Span(DateTimeOffset s, DateTimeOffset e) => e < s ? throw new ArgumentException("end before start") : e - s;`. Check 23:50Z to 00:10Z the next day is 20 minutes, equal start and end is `TimeSpan.Zero`, and reversed inputs throw.',
            why="Subtracting full `DateTimeOffset` values includes the date, so midnight is not a special case. The guard turns a negative duration into a rejection when the domain forbids it.",
            wrong="Computing from `e.TimeOfDay - s.TimeOfDay` drops the dates: 00:10 minus 23:50 is minus 23 hours 40 minutes, so the guard rejects a valid 20-minute interval as ending before its start.",
            verify="Run the three checks with fixed UTC values, catching `ArgumentException` for the reversed pair.",
        ),
        6: dict(
            explain="For future appointments, store the local date and time plus a zone ID such as `America/New_York`, and compute the UTC instant when needed. Display by converting to the viewer's zone. For events that already happened, store the UTC instant.",
            why="A 09:00 meeting should stay at 09:00 local even if daylight-saving rules change before it happens. Storing the zone keeps that intent; converting at display time keeps viewers correct. Invalid and repeated local times must be handled at booking.",
            wrong="Converting the booking to a UTC instant at creation freezes the rules in force that day. If they change, the stored instant now displays as 08:00 or 10:00 local, and nothing in storage records that 09:00 was intended.",
            verify='With `var ny = TimeZoneInfo.FindSystemTimeZoneById("America/New_York");`, check `ny.IsInvalidTime(new DateTime(2025, 3, 9, 2, 30, 0))` is true and `ny.IsAmbiguousTime(new DateTime(2025, 11, 2, 1, 30, 0))` is true, and make the booking code reject or clarify both.',
        ),
    },
    34: {
        1: dict(
            explain="`count++` is a read, an add and a write. Two tasks can both read 57 and both write 58, losing one increment, so four tasks of 100 can end below 400. `Interlocked.Increment(ref count)` performs the read, add and write as one indivisible operation, so the total is exactly 400.",
            why="The processor's atomic increment never exposes an intermediate value, so no other task can read between the load and the store.",
            wrong="Marking a field `volatile` and keeping `count++` does not help. `volatile` makes each read and write visible, but the three steps can still interleave, so updates are still lost.",
            verify="Swap in `count++` and raise the loop to 100,000 per task; repeated runs usually end below 400,000 and the check throws. With `Interlocked.Increment` every run is exact. With only 100 iterations a lost update is rare, which is why the count is raised.",
        ),
        2: dict(
            explain='Add ten tasks calling `counts.AddOrUpdate("b", 1, (_, previous) => previous + 1)` to the same `Task.WhenAll`, then check `counts["a"] == 20 && counts["b"] == 10`.',
            why="Each `AddOrUpdate` call is atomic for its key, and updates to `a` and `b` never affect each other, so the two counts are independent.",
            wrong='Writing `counts["b"] = counts.GetValueOrDefault("b") + 1;` uses two thread-safe calls, but the read and the write are separate. Two tasks can read 4 and both store 5, so `b` sometimes ends below 10.',
            verify="Run the combined example ten times in a loop and check both counts every time.",
        ),
        3: dict(
            wrong="Replacing `AddOrUpdate` with `counts.TryGetValue(w, out int c); counts[w] = c + 1;` keeps the dictionary itself consistent but loses updates between the read and the write, so `a` can end at 2.",
            verify='The block checks `a` is 3 and `b` is 1. Scale it to `Enumerable.Repeat("a", 10_000)` and check `counts["a"] == 10_000` on several runs; the read-then-write version usually falls short.',
        ),
        4: dict(
            explain='A delegate such as `(k, old) => { mailer.Send($"{k} updated"); return old + 1; }` can run more than once for one logical update. `AddOrUpdate` reads the value, calls the delegate, then tries to store; if another task changed the value first, it calls the delegate again. Send after the call, using its return value.',
            why="`ConcurrentDictionary` runs the delegate outside its internal lock and retries on contention, so only the returned value is guaranteed to correspond to one successful update.",
            wrong="Wrapping `mailer.Send` in a `lock` inside the delegate serializes the sends but does not stop the retry, so a retried update still sends a second message.",
            verify='Count delegate calls with `Interlocked.Increment` during 20 concurrent updates of one key. Under contention the call count can exceed 19 while `counts["a"]` is 20; messages sent after the call are exactly 20.',
        ),
        5: dict(
            explain='Check `counts.AddOrUpdate("x", 1, (_, p) => p + 1) == 1` for an absent key, and a second call returns 2. For `GetOrAdd`, check the factory is not called when the key already exists.',
            why="`AddOrUpdate` uses `addValue` when the key is absent and the update function only when it is present, so the two cases exercise different code.",
            wrong="Passing `0` as `addValue` passes every test that only uses already-present keys, but the first word is then counted as 0 and every frequency is one too low.",
            verify="Run the absent and present checks on a fresh dictionary, then change `addValue` to 0 and confirm the absent-key check throws.",
        ),
        6: dict(
            explain="A transfer of 10 from A to B done as two atomic updates, `A - 10` and then `B + 10`, leaves a moment where the money is in neither account. A concurrent audit sums 90 instead of 100, and an exception between the calls loses the 10 permanently.",
            why="Atomicity per key protects one location. The invariant `A + B == 100` spans two locations, so both updates need one lock or a transaction that the audit also respects.",
            wrong='Making the debit conditional with `TryUpdate("A", old - 10, old)` stops overdrafts but does not join the two steps. A reader between the debit and the credit still sees 90.',
            verify="Run 1,000 transfers in one task while another task sums both balances repeatedly. Without a shared lock some sums are 90; with one lock around both the transfer and the audit, every sum is 100.",
        ),
    },
    35: {
        1: dict(
            explain="`values` holds 1, 2 and 3 at indices 0, 1 and 2. `values.AsSpan(1, 1)` starts at index 1 with length 1, so `middle[0]` is the same storage as `values[1]`. Doubling it changes the array to 1, 4, 3.",
            why="A span is a reference to a starting element plus a length. It shares the array's memory, so a write through the span is a write to the array.",
            wrong="Treating the slice like `values.Skip(1).Take(1).ToArray()` predicts an unchanged array. That LINQ chain copies the element, but `AsSpan` does not copy anything.",
            verify="Check `values.AsSpan(1, 1)[0] == values[1]`, then set `middle[0] = 9` inside a helper and check `values[1] == 9`.",
        ),
        2: dict(
            explain="Use `Span<int> middle = values.AsSpan(1, 2);` and double each element with `for (int i = 0; i < middle.Length; i++) middle[i] *= 2;`. The array becomes 1, 4, 6.",
            why="The second argument is a length, not an end index, so `(1, 2)` covers indices 1 and 2.",
            wrong="Reading the second argument as an end index and writing `AsSpan(1, 3)` asks for indices 1 through 3. The array has no index 3, so the call throws `ArgumentOutOfRangeException` before anything is doubled.",
            verify="Check `values.SequenceEqual(new[] { 1, 4, 6 })` and that `values[0]` is still 1.",
        ),
        3: dict(
            wrong="`text.ToString().Split(separator).Length - 1` returns the same counts, including 0 for empty text, but it allocates a string and an array of substrings, which is what accepting a span was meant to avoid.",
            verify='The block checks `a,b,c` and an empty span. Add `",,"` expecting 2. To see that the span version allocates nothing, call it once to warm up, then check `GC.GetAllocatedBytesForCurrentThread()` is unchanged across a second call.',
        ),
        4: dict(
            explain="In `async Task<int> First(int[] data) { Span<int> view = data.AsSpan(); await Task.Delay(1); return view[0]; }` the compiler rejects using `view` after the `await`. Pass `Memory<int>` instead and take `.Span` only in synchronous code after the await.",
            why="Locals that live across an `await` are stored in a heap-allocated state machine. `Span<T>` is a ref struct that may point at stack memory, so it cannot be stored on the heap.",
            wrong="Copying with `int[] copy = view.ToArray();` before the await compiles, but any later write goes to the copy, so the caller's buffer never changes when the method was meant to fill it.",
            verify="Compile the span version and read the error about preserving a `Span<int>` across `await`. The `Memory<int>` version that writes `memory.Span[0] = 9` after the await changes `data[0]` to 9.",
        ),
        5: dict(
            explain="With `int[] values = { 1, 2, 3 }`, check `values.AsSpan(3, 0).IsEmpty` is a valid empty slice at the end, and that `values.AsSpan(4, 0)` and `values.AsSpan(2, 2)` throw `ArgumentOutOfRangeException`. Also check `SumDigits(ReadOnlySpan<char>.Empty) == 0`.",
            why="A slice is valid when `start <= Length` and `start + length <= Length`. Start 3 with length 0 satisfies both; start 4 and the end index 4 of `(2, 2)` do not.",
            wrong="A guard such as `if (start >= values.Length) throw` rejects `(3, 0)`, yet that empty slice is exactly what slicing the remainder after a final separator produces, so a parser using the guard fails on input ending with a comma.",
            verify="Run the empty-slice check and catch `ArgumentOutOfRangeException` for the two invalid calls.",
        ),
        6: dict(
            explain="The synchronous parser takes `ReadOnlySpan<char>`, so it accepts strings, arrays and `stackalloc` buffers without copying. The asynchronous owner rents a `byte[]` from `ArrayPool<byte>.Shared`, exposes it as `Memory<byte>` to `Stream.ReadAsync`, and returns it to the pool in `Dispose`.",
            why="`Memory<T>` can be stored in fields and survive an `await`, which `Span<T>` cannot. Having one class own the rented array gives one clear point where it is returned.",
            wrong="Returning the rented array to the pool in a `finally` while a stored `Memory<byte>` still refers to it lets the next `Rent` hand the same array to another caller, so two components write into one buffer.",
            verify="Parse `\"42\"` from a string and from `stackalloc char[] { '4', '2' }` and check both give 42. For the owner, read a known `MemoryStream` through `owner.Memory`, check the bytes, then dispose it.",
        ),
    },
    36: {
        1: dict(
            explain="`Rent(3)` promises an array of at least 3 elements. The shared pool rounds requests up to bucket sizes, so `rented.Length` is typically 16. The logical length is 3: the number of slots this code wrote and is allowed to read, which is why the sum uses `AsSpan(0, 3)`.",
            why="Only the logical range holds values this code wrote. Slots 3 and beyond may be zero or may hold whatever a previous renter left there.",
            wrong="Summing `rented.Sum()` or looping to `rented.Length` reads the extra capacity. It happens to give 9 when those slots are zero, which hides the bug until a previous renter leaves data behind.",
            verify="Inside the `try`, write 100 into `rented[rented.Length - 1]`. The logical sum stays 9 while `rented.Sum()` becomes 109.",
        ),
        2: dict(
            explain="Keep one variable, `int count = 5;`, use it for `Rent(count)`, for the loop that writes `i + 1` into slots 0 to 4, and for `AsSpan(0, count)`. The sum is 15.",
            why="Driving the request, the initialization and the read from one value keeps the logical region identical in all three places.",
            wrong="Changing only `Rent(3)` to `Rent(5)` while the read still says `AsSpan(0, 3)` sums 1 + 2 + 3 = 6 and silently ignores two initialized slots.",
            verify="Check the sum is 15, then set `count = 17`: the array is typically 32 long, yet the sum is 153, the total of 1 to 17.",
        ),
        3: dict(
            wrong="Returning the buffer first and summing afterward, `Return(buffer, clearArray: true); return buffer.AsSpan(0, count).ToArray().Sum();`, reads an array the pool already owns. The clear has zeroed it, so `SumPooled(4)` returns 0 instead of 10.",
            verify="The block checks `SumPooled(4) == 10`. Add `SumPooled(1) == 1` and `SumPooled(100) == 5050`; the second needs a larger bucket and still uses only the first 100 slots.",
        ),
        4: dict(
            explain="Two defects. Reading past the logical length: rent 4, fill with 7, return without clearing, rent 4 again on the same thread, and `buffer[0]` is likely 7 rather than 0. Returning twice: `Return(buffer); Return(buffer);` can let two later `Rent` calls hand out the same array.",
            why="The pool does not track who owns an array and does not reject a second return. Each caller must initialize what it reads and return each rental exactly once.",
            wrong="Wrapping the second `Return` in a `try` and expecting an exception to flag the mistake does not work, because the pool accepts the duplicate silently. The damage appears later, in unrelated code that shares the array.",
            verify="After a double return, `var x = Rent(4); var y = Rent(4);` and print `ReferenceEquals(x, y)`; it is likely true, which never happens with buffers returned once. Rent with a fresh `ArrayPool<int>.Create()` to see initial zeros for comparison.",
        ),
        5: dict(
            explain="Wrap a pool created with `ArrayPool<int>.Create()` in a small `CountingPool : ArrayPool<int>` that counts `Rent` and `Return` calls and forwards them. Make the computation throw at element 2, catch the exception, and check one rent and one return.",
            why="A counting pool gives deterministic evidence. Checking whether the shared pool later hands back the same array depends on per-thread caching and can vary between runs.",
            wrong="Placing `Return` after the computation instead of in `finally` skips it when the throw happens. Nothing crashes, because the pool simply allocates new arrays later, so the leak is invisible without counting.",
            verify="Check `rents == 1 && returns == 1` after the exception. Move `Return` out of `finally` and the same check throws because `returns` is 0.",
        ),
        6: dict(
            explain="Pool a 128 KB parse buffer that a service allocates on every request, because arrays over 85,000 bytes go on the large object heap and are collected only in generation 2. State the contract: the buffer is rented and returned within one synchronous call and is never stored or captured by asynchronous work.",
            why="Pooling pays off when measured allocation and generation 2 collections drop while results stay identical. The contract keeps the ownership risk small enough to review.",
            wrong="Pooling a 32-byte array used once per request adds `Rent` and `Return` calls and an ownership rule for almost no saving, because small short-lived arrays are cheap generation 0 allocations.",
            verify="Run a fixed workload of 10,000 parses with `new byte[131072]` and again with the pool. Compare `GC.GetAllocatedBytesForCurrentThread()` and `GC.CollectionCount(2)`, and check both versions produce identical parse results.",
        ),
    },
    37: {
        1: dict(
            explain="For `{ 2, 4, 6, 8 }`: target 2 takes 1 comparison, target 8 takes 4, and an absent target such as 9 also takes 4, because the loop must check every element before it can report absence.",
            why="`comparisons++` runs once per visited element and `break` stops on the first match, so the count equals the matched position, or the length when nothing matches.",
            wrong="Predicting that an absent target is cheap because nothing is found treats absence as an early exit. Without a match there is no `break`, so absence is a worst case.",
            verify="Wrap the loop as `int Count(int target)` and check `Count(2) == 1`, `Count(8) == 4` and `Count(9) == 4`.",
        ),
        2: dict(
            explain="With 8 values `{ 2, 4, ..., 16 }`, the worst case, last element or absent, needs 8 comparisons. Doubling the input from 4 to 8 doubles the worst case: linear growth.",
            why="Each element is compared at most once, and the worst case visits all of them, so the count grows in proportion to the length.",
            wrong="Predicting 5 comparisons assumes the search halves its range like binary search. This loop has no ordering logic, and on unsorted data halving would not even be correct.",
            verify="Check `Count(16) == 8` and `Count(17) == 8` on the 8-element array, and `Count(2) == 1` still.",
        ),
        3: dict(
            wrong='Building the index with `new HashSet<string>(names)` uses the default ordinal, case-sensitive comparer. `"PEAR"` and `"fig"` are then not found, `indexHits` is 0 while `scanHits` is 2, and the `same answers` check throws.',
            verify='The block checks both approaches find 2. Add `"APPLE"` to the queries and expect 3 from both; that shows the comparer, not the data, decides membership.',
        ),
        4: dict(
            explain="For a one-shot workload, one query against 1,000 names, a benchmark that builds the `HashSet` outside the timed region and times only `Contains` shows the index winning. The real job must also pay for construction: 1,000 hashes and inserts, versus at most 1,000 comparisons for one scan.",
            why="The measured region must match the workload. Construction is amortized only across many queries; with one query it is the dominant cost.",
            wrong="Running the timed `Contains` call 1,000 times to get a steadier number measures a many-query workload. The figure is more stable but still answers a different question.",
            verify="Count operations instead of timing: include the 1,000 insertions with the single lookup and compare with the scan's comparison count. The scan wins for one query; the index wins once queries are numerous.",
        ),
        5: dict(
            explain='With `names = { "a", "A", "a" }` and `OrdinalIgnoreCase`, the set holds 1 entry, yet the scan and the index both find `"A"`. With an empty query array both report 0 hits, and a query of `""` is not found.',
            why="The set collapses duplicates under its comparer, but membership answers are unchanged, so hit counts still agree.",
            wrong="Using `index.Count` as the number of names loaded reports 1 instead of 3. A check `index.Count == names.Length` fails on any input with duplicates under the comparer.",
            verify='Check `index.Count == 1`, that `scanHits == indexHits` for queries `{ "A", "" }`, and that both are 0 for `Array.Empty<string>()`.',
        ),
        6: dict(
            explain="Workload: 10,000 names with 1, 100 and 10,000 queries, half of them hits. Correctness: before any timing, check the scan and the index return identical hit counts for each case. Warmup: run each method before measuring, ideally with BenchmarkDotNet in a separate project. Allocations: record bytes per operation for each method.",
            why="Each element removes one distortion: wrong answers, JIT compilation and tiering, and allocation costs that show up later as collections. Reporting the median of many iterations avoids trusting one sample.",
            wrong="Timing the first call of each method with one `Stopwatch` measures JIT compilation as much as the algorithm, and the order in which the methods run can decide the winner.",
            verify="Break the index comparer on purpose and confirm the plan's correctness check fails before any time is reported.",
        ),
    },
    38: {
        1: dict(
            explain="`\\A` anchors at the start of the input. `[a-z]` requires one lowercase ASCII letter first. `[a-z0-9_]{0,15}` allows up to 15 more letters, digits or underscores. `\\z` anchors at the absolute end. Total length is 1 to 16. `NonBacktracking` gives linear-time matching, and the one-second timeout is a final guard.",
            why="With both anchors, the whole input must match the pattern, so no prefix or suffix outside the allowed characters can slip through.",
            wrong='Using `$` instead of `\\z` looks equivalent, but `$` also matches before a final newline, so `"report\\n"` would be accepted with a trailing line break.',
            verify='Check `IsMatch("a")`, a 16-character identifier accepted, a 17-character one rejected, and `"report\\n"` rejected.',
        ),
        2: dict(
            explain='For a maximum of 8 characters, change the quantifier to `{0,7}`. Check `"abcdefgh"` (8) is accepted and `"abcdefghi"` (9) is rejected.',
            why="The first letter is matched by `[a-z]` outside the quantifier, so the quantifier's maximum is one less than the total.",
            wrong="Writing `{0,8}` for an 8-character maximum allows 9 characters, an off-by-one that a test using only short names never sees.",
            verify="Check both boundary values with the new pattern, then temporarily use `{0,8}` and confirm the 9-character check throws.",
        ),
        3: dict(
            wrong="Folding the reserved word into the pattern with a lookahead, `\\A(?!admin\\z)[a-z]...`, fails at construction: `RegexOptions.NonBacktracking` does not support lookarounds and throws `NotSupportedException`.",
            verify='The block checks `report_2`, `admin` and `2report`. Add `!Valid("Admin")`, rejected by shape, and `Valid("admin2")`, accepted because the reserved check is an exact ordinal match; decide whether prefixes should also be reserved.',
        ),
        4: dict(
            explain='Without anchors, `[a-z][a-z0-9_]{0,15}` finds `report` inside `"report!"` and inside `"2report"`, so `IsMatch` returns true for both. Add `\\A` and `\\z` so the whole input must match.',
            why="`IsMatch` searches for a match anywhere in the input unless the pattern pins the start and end.",
            wrong='Adding only the start anchor, `\\A[a-z][a-z0-9_]{0,15}`, rejects `"2report"` but still accepts `"report!"`, because the trailing `!` is never examined.',
            verify="With the unanchored pattern, the Example A `rejected shapes` check throws. With both anchors it passes.",
        ),
        5: dict(
            explain='Check `"report\\n"` is rejected, `""` is rejected because one letter is required, `"a" + new string(\'b\', 15)` (16 characters) is accepted and `"a" + new string(\'b\', 16)` (17 characters) is rejected.',
            why="`\\z` refuses the trailing newline, the leading `[a-z]` refuses empty input, and the quantifier caps the length at 16.",
            wrong='Calling `input.Trim()` before validation accepts `"report\\n"`, but if the original string is then stored, the saved identifier still contains the newline that validation never saw.',
            verify="Run the four checks; all pass silently. Replace `\\z` with `$` and confirm the newline check now throws.",
        ),
        6: dict(
            explain="For a nested format such as `(a,(b,c))`, write a small recursive descent parser with a depth limit. It can report errors such as `expected ')' at position 7`, and the depth limit bounds the work.",
            why="Matching nesting needs counting, which a regular expression cannot express; .NET balancing groups exist but are hard to review and are not supported by `NonBacktracking`. A parser makes the grammar and the error positions explicit.",
            wrong='A pattern like `\\A\\(.*\\)\\z` accepts `"((a)"`, which is unbalanced, and `"(a)(b)"`, which is two groups, because `.*` cannot track depth.',
            verify="Check the parser accepts `(a,(b,c))`, rejects `((a)` with an error at the end of input, and rejects 1,000 nested parentheses with a depth error instead of a `StackOverflowException`.",
        ),
    },
    39: {
        1: dict(
            explain='Transport: `GetAsync` returns the response produced by `FixtureHandler`, with no network. Status: `EnsureSuccessStatusCode` throws `HttpRequestException` for non-2xx. Decoding: `JsonDocument.Parse` throws `JsonException` for malformed text. Schema: `GetProperty("count")` throws `KeyNotFoundException` when missing, and `GetInt32` throws when the value is not a number.',
            why="Each boundary has its own failure type, so a caller can report which fact failed: the response, the status, the syntax or the shape.",
            wrong="Catching `Exception` around the whole call and reporting `service unreachable` merges all four boundaries. A 503, a truncated body and a renamed field then look like the same outage.",
            verify='Run Example A with bodies `{`, `{}` and `{"count":"3"}` and catch `JsonException`, `KeyNotFoundException` and `InvalidOperationException` respectively; the 503 fixture gives `HttpRequestException`.',
        ),
        2: dict(
            explain='Use `new FixtureHandler(HttpStatusCode.OK, "{\\"total\\":3}")`. Status and parsing succeed, and `GetProperty("count")` throws `KeyNotFoundException`. Classify it as a contract failure: the server answered with valid JSON of the wrong shape.',
            why="The transport and syntax layers both succeeded, so neither retrying nor reporting malformed JSON fits. The fix belongs with whoever owns the response schema.",
            wrong='`root.TryGetProperty("count", out var c) ? c.GetInt32() : 0` turns the broken contract into a valid-looking count of 0, which downstream code cannot distinguish from an empty store.',
            verify="Catch `KeyNotFoundException` and check it was thrown, or check `TryGetProperty` returns false and report `count missing`.",
        ),
        3: dict(
            wrong="Creating `new HttpClient()` inside `GetCountAsync` makes the fixture impossible to inject, so the test would resolve `example.invalid` and fail with `HttpRequestException`. Creating a client per call also wastes connections in production.",
            verify="The block checks 4. Add `using var cts = new CancellationTokenSource(); cts.Cancel();` and check that `GetCountAsync(client, cts.Token)` throws an `OperationCanceledException`, proving the token reaches the request.",
        ),
        4: dict(
            explain="`if (!response.IsSuccessStatusCode) return 0;` reports a 503 as a count of 0, so a dashboard shows an empty store during an outage. Let `EnsureSuccessStatusCode` throw, or return a result type that carries the status.",
            why="Receiving a response and the request succeeding are separate facts. A count is meaningful only after the status confirms success.",
            wrong="Returning -1 instead of 0 is still a number in the count's range. Any caller that sums or averages counts treats the outage as data.",
            verify="With the Example B fixture, the buggy method returns 0 and a check expecting `HttpRequestException` throws. The fixed method raises the exception and the check passes.",
        ),
        5: dict(
            explain='Body `{"count":` makes `JsonDocument.Parse` throw a `JsonException`. Body `{"count":"3"}` parses, but `GetInt32` throws `InvalidOperationException` because the value kind is `String`. Body `{"count":3.5}` throws `FormatException`.',
            why="Syntax errors are detected by the parser; type errors are detected only when a value is read as a specific type. Tests need a fixture for each.",
            wrong='Reading with `int.Parse(c.ToString())` accepts the string `"3"` and returns 3, silently accepting a server that broke the numeric contract.',
            verify="Run the three fixtures through the Task 3 method and catch the three exception types separately.",
        ),
        6: dict(
            explain="Retry reads (`GET`) on 503, 429 (honoring `Retry-After`), 408 and transport failures, up to 3 attempts with exponential backoff and jitter. Never retry 400, 401 or 404. For a `POST` that creates an order, a timeout leaves the outcome unknown: retry only with an idempotency key the server deduplicates, or query the order status first.",
            why="Repeating a safe read cannot change server state. Repeating a write whose first attempt may have succeeded can create a second order.",
            wrong="Retrying every non-2xx and every timeout uniformly sends a second `POST` after a timeout, and the customer is charged twice when the first request had in fact succeeded.",
            verify="Write a handler that returns 503 twice and then 200: the `GET` succeeds with exactly 3 handler calls. For a `POST` without an idempotency key, a timeout fixture must produce exactly 1 handler call.",
        ),
    },
    41: {
        1: dict(
            explain='`ValidateCreate("pear", 3)` returns `ApiDecision(201, "accepted")`: a nonblank name and a nonnegative quantity. In ApiLab the matching request is `POST /items` with `{"id":"pear-1","name":"pear","quantity":3}`. It answers `201 Created` with `Location: /items/pear-1` and echoes the stored item as JSON.',
            why="The status says a resource was created, the Location header says where to fetch it, and the body confirms what was stored. A client can act on all three without guessing.",
            wrong="Returning `200` with the text `accepted` for a create also looks successful, but a client that follows the `Location` header of a 201 has nothing to follow, and the response cannot be told apart from a read.",
            verify="The Example A check `result.Status == 201` passes. Against ApiLab, `curl -i` on the POST prints `HTTP/1.1 201 Created` and `Location: /items/pear-1`.",
        ),
        2: dict(
            explain='Add a branch before the success case: `quantity > 1000 ? new(400, "quantity above 1000")`. Document that 1000 is accepted and 1001 is rejected, and apply the same rule in the ApiLab POST handler so the kernel and the host agree.',
            why="An oversized quantity is a client input error, the same category as a negative quantity, so it maps to 400 with a message naming the rule that failed.",
            wrong="Mapping the rule to `413 Payload Too Large` sounds fitting, but 413 describes the size of the request body. A 60-byte JSON body with `quantity: 5000` is not too large, and clients that handle 413 by shrinking uploads would react incorrectly.",
            verify='Check `ValidateCreate("pear", 1000).Status == 201` and `ValidateCreate("pear", 1001).Status == 400`, then confirm Example B still passes.',
        ),
        3: dict(
            explain="Copy `fixtures/ApiLab` into an ignored workspace and run `dotnet restore --configfile NuGet.Config`, `dotnet build --no-restore` and `dotnet run --no-build --urls http://127.0.0.1:5080`. In a second terminal, run the six `curl -i` commands from the README.",
            why="The six requests cover health, create, read, duplicate create, invalid create and unknown read, so each branch of the handlers in `Program.cs` produces one observed status.",
            wrong="Running `dotnet run` without `--urls` lets the host pick its configured default URL, so the curl commands aimed at port 5080 fail to connect and look like a broken API rather than a different port.",
            verify="Expect 200, 201, 200, 409, 400 and 404 in that order. Stop the server with Ctrl+C, start it again, and `GET /items/pear-1` returns 404 because the inventory was in memory.",
        ),
        4: dict(
            explain='A handler that writes `await context.Response.WriteAsync("ok")` and only then validates has already sent a 200 status line and headers. When validation fails, `context.Response.StatusCode = 400` throws `InvalidOperationException` because the response has started. Validate first, then choose the status, then write the body.',
            why="HTTP sends the status before the body. Once `Response.HasStarted` is true, ASP.NET Core cannot change the status, so the decision must be final before any bytes are written.",
            wrong="Catching the `InvalidOperationException` and appending `error` to the body leaves the client with status 200 and a body that disagrees with it. Any client that checks only the status records the invalid item as created.",
            verify="Check `context.Response.HasStarted` is false at the point where the status is set. With the kernel, `ValidateCreate` returns its decision before any output, which Example B checks.",
        ),
        5: dict(
            explain='Missing identity: `ValidateCreate("", 3)` and `ValidateCreate("   ", 3)` return 400. Zero quantity: `ValidateCreate("pear", 0)` returns 201, because the rule is `quantity < 0`. Unknown lookup: the kernel has no lookup, so test ApiLab, where `GET /items/missing` returns 404.',
            why="Whitespace-only names are rejected by `string.IsNullOrWhiteSpace`, zero is a real stock level, and a well-formed request for an absent resource is a 404 rather than a client input error.",
            wrong="Writing the rule as `quantity <= 0` rejects an empty bin that the inventory needs to record. Mapping an unknown id to 400 blames the client for a valid request.",
            verify="Check the three kernel decisions, then `curl -i http://127.0.0.1:5080/items/missing` prints `HTTP/1.1 404 Not Found`.",
        ),
        6: dict(
            explain="Add `PUT /items/{id}` that stores the full representation sent: if the id exists, replace it and return 200; otherwise create it and return 201. Sending the same body twice leaves the same state. `POST /items` stays non-idempotent: in ApiLab the second identical POST returns 409 because `TryAdd` refuses the duplicate.",
            why="PUT means the item should now look exactly like this body, so a retried PUT after a timeout is harmless. POST means add one, so the server must detect a repeat.",
            wrong="Implementing PUT as add `quantity` to the stored item makes a retried request after a lost response raise the stock from 3 to 6, which breaks the idempotency that clients and proxies assume for PUT.",
            verify="Send the same PUT with quantity 3 twice, then `GET /items/pear-1` shows quantity 3. Repeating the POST gives 201 then 409.",
        ),
    },
    45: {
        1: dict(
            explain='Example A checks at run time: `GetProperty` returns `PropertyInfo?`, and `GetProperty("Missing")` compiles but returns null. `nameof(Metric.Count)` is the only compile-time check there. Example B is checked entirely by the compiler: `value.Count` must exist and be an `int`, or `Func<Metric, int>` does not compile.',
            why="A string member name is opaque to the compiler, while a lambda member access is resolved during compilation, so typos and type changes become build errors.",
            wrong="Assuming `nameof` makes the reflection lookup safe overlooks that it only checks the name at build time. The result is still nullable, and trimming or a renamed member reached through a different string can still produce null at run time.",
            verify='Change Example B to `value.Cont` and the build fails with CS1061. Change Example A to `GetProperty("Cont")` and it compiles, then the `known metadata` check throws.',
        ),
        2: dict(
            explain='Inspect `typeof(string).GetProperty(nameof(string.Length))`; its `PropertyType` is `typeof(int)`, and `GetValue("pear")` returns 4. For absence, `if (typeof(string).GetProperty("Size") is not { } size)` reports `Size missing` instead of dereferencing.',
            why="The pattern `is not { } size` both tests for null and binds the non-null value, so the code that reads the property runs only when it exists.",
            wrong='Writing `typeof(string).GetProperty("Size")!.GetValue("pear")` silences the nullable warning with `!`, and the missing property becomes a `NullReferenceException` at run time.',
            verify='Check `typeof(string).GetProperty("Length")?.PropertyType == typeof(int)`, that `GetProperty("Size")` is null, and that `typeof(Metric).GetProperties().Length == 1`, because the record\'s synthesized `EqualityContract` property is protected.',
        ),
        3: dict(
            wrong='The string version `metrics.Sum(m => (int)typeof(Metric).GetProperty("count")!.GetValue(m)!)` compiles, but `GetProperty` is case-sensitive by default. It returns null for `"count"`, and the `!` turns that into a `NullReferenceException` at run time.',
            verify="The block checks the total is 7. Add `new Metric(0)` and expect 7 again; rename `Count` to `Total` in the record and the build fails at `metric.Count`, which is the point of the typed projection.",
        ),
        4: dict(
            explain="Reading a type name and property name from configuration and calling `Type.GetType(typeName)?.GetProperty(propertyName)` works in a normal run. With `-p:PublishTrimmed=true`, the trimmer cannot see which members those strings name, so it may remove them and the calls return null. Annotate the parameter with `[DynamicallyAccessedMembers(DynamicallyAccessedMemberTypes.PublicProperties)]` or replace the lookup with a typed projection.",
            why="Trimming keeps only what static analysis proves is used. `typeof(Metric).GetProperty(nameof(Metric.Count))` uses constants it can follow, but names from configuration are unknown at publish time.",
            wrong="Suppressing the trim analysis warnings (IL2xxx) with `<NoWarn>` or `[UnconditionalSuppressMessage]` makes the publish look clean while the members are still removed, so the failure appears in production instead of at publish time.",
            verify="Run `dotnet publish -c Release -r linux-x64 -p:PublishTrimmed=true` in a separate project and read the trim warnings. Run the trimmed output and check that the configured lookup is not null.",
        ),
        5: dict(
            explain='Write `int? ReadInt(object target, string name)`: return null when `GetProperty(name)` is null or when `PropertyType != typeof(int)`, otherwise return `(int)property.GetValue(target)!`. Test with `Metric(4)` and `"Count"`, with `"Missing"`, and with `record Wide(long Count)`.',
            why="Checking `PropertyType` before unboxing turns both kinds of surprise, an absent member and a member of another type, into one explicit policy result.",
            wrong="Unboxing without the type check, `(int)property.GetValue(target)!`, throws `InvalidCastException` for `Wide(5)`, because a boxed `long` can be unboxed only as `long`, even though 5 fits in an `int`.",
            verify='Check `ReadInt(new Metric(4), "Count") == 4`, `ReadInt(new Metric(4), "Missing") is null` and `ReadInt(new Wide(5), "Count") is null`.',
        ),
        6: dict(
            explain="Target `linux-x64`, built on a Linux x64 host with `clang` and the zlib development package installed. Publish with `dotnet publish -c Release -r linux-x64 -p:PublishAot=true`. Runtime checks: the native binary prints the same `csharp-045: passed` marker as the managed run, the publish reports no unreviewed AOT or trim warnings, and startup time and file size are compared with a framework-dependent publish.",
            why="Native AOT compiles ahead of time for one operating system and architecture and needs the platform linker, so the plan must name both and compare behavior, not only build success.",
            wrong="Publishing from macOS with `-r linux-x64 -p:PublishAot=true` and expecting a Linux binary fails, because Native AOT does not support cross-OS compilation. The experiment has to run on the target OS or in a matching container.",
            verify="`file` on the output reports an ELF 64-bit x86-64 executable, running it prints the pass marker, and the publish log shows zero warnings.",
        ),
    },
    48: {
        1: dict(
            explain='Example A: `b=2`, `a=3` and `b=4` all pass validation; grouping gives `b` 6 and `a` 3, and ordinal ordering yields `a=3;b=6` with 0 rejected. Example B: `("", 2)` fails `IsNullOrWhiteSpace`, `("a", -1)` fails `Quantity < 0`, and `("b", 0)` is accepted, so the text is `b=0` with 2 rejected.',
            why="Every row takes exactly one branch of the `if`, so the valid count plus the rejected count always equals the input count.",
            wrong='Assuming `("b", 0)` disappears because it adds nothing predicts text `""`. The rule rejects only negative quantities, so a zero row creates its own group.',
            verify="Add `Check(valid.Count + rejected == rows.Count())` inside a copy of `Report` (over a materialized array) and run both examples.",
        ),
        2: dict(
            explain='Add `new Row("B", 1)` to Example A. By hand: `B` is a new group with 1, and ordinal order puts uppercase `B` (code 66) before `a` (97). The expected text is `B=1;a=3;b=6` with 0 rejected.',
            why="The expected value is derived from the input and the rules, not from the program, so the check can catch a defect in the code.",
            wrong="Running the program and pasting whatever it prints into the expected string makes the test agree with the code by construction. If `OrderBy` used a case-insensitive comparer, its `a=3;b=6;B=1` would be enshrined even though the contract says ordinal.",
            verify='Check `report.Text == "B=1;a=3;b=6"`. Temporarily switch the comparer to `StringComparer.OrdinalIgnoreCase`: `b` and `B` then tie, the stable sort keeps `b` first, the text becomes `a=3;b=6;B=1` and the check fails.',
        ),
        3: dict(
            explain='Build DomainLab with its README commands and expect `DomainLab: seven contract checks passed`. In ApiLab.csproj add `<ProjectReference Include="../DomainLab/Domain/Domain.csproj" />` (adjusting the path to your copy) and map `POST /reports` to `Journey.Domain.Inventory.Summarize`, converting each ApiLab `Item` with `new Journey.Domain.Item(i.Name, i.Quantity)`.',
            why="The domain library keeps the validation and aggregation rules, and the endpoint only converts HTTP input and maps the result, so the seven checks still cover the logic the API uses.",
            wrong="Copying the `IsNullOrWhiteSpace` and negative-quantity checks into the endpoint and passing only valid rows to `Summarize` makes `Rejected` always 0, and leaves two copies of the rule that can drift.",
            verify='POST `[{"id":"1","name":"pear","quantity":2},{"id":"2","name":"","quantity":9}]` to `/reports` and expect 200 with totals `pear` 2 and `rejected` 1.',
        ),
        4: dict(
            explain='Introduce `.Select(group => group.Key + "=" + group.First().Quantity)` in place of `group.Sum`. Example A then prints `a=3;b=2`, and the `stable report` check throws. The diagnosis: duplicate names were grouped but only the first quantity was kept.',
            why="Example A deliberately contains `b` twice, so any aggregation that does not sum the group produces a different value for `b`.",
            wrong='"Fixing" duplicates with `rows.Distinct()` before reporting collapses rows that are equal by value, because `Row` is a record. `Row("b", 2)` twice becomes one row, and `b` reports 2 instead of 4.',
            verify='Restore `group.Sum`, then check `Report(new[] { new Row("b", 2), new Row("b", 2) }).Text == "b=4"`.',
        ),
        5: dict(
            explain='Empty: `Text == ""` and `Rejected == 0`. Malformed: `Row("  ", 1)` and `Row("a", -5)` are rejected. Overflow: `Row("x", int.MaxValue)` plus `Row("x", 1)` throws `OverflowException`, because `Enumerable.Sum` over `int` is checked. Repeated operation: calling `Report` twice on the same array gives equal tuples.',
            why="Each boundary has a defined outcome: empty is a valid report, malformed rows are counted, overflow is a visible failure, and the function is pure, so repeating it changes nothing.",
            wrong="Replacing `Sum` with a manual `total += row.Quantity` loop in an unchecked context wraps to `-2147483648` and prints `x=-2147483648` as if it were a real total.",
            verify="Check each case, catching `OverflowException` for the overflow input, and compare two calls with `==` on the tuples.",
        ),
        6: dict(
            explain="The README lists the DomainLab and ApiLab restore, build and run commands with their expected outputs, an architecture section (Domain owns rules, Checks owns examples, ApiLab owns HTTP mapping), failure policies (400 invalid, 409 duplicate id, overflow as a visible error), the tests, the limits (in-memory state lost on restart, loopback only, no authentication) and one next extension such as per-item rejection reasons.",
            why="A reviewer can rebuild the project, rerun the evidence and see what is unsupported without reading the code first.",
            wrong="Documenting `dotnet test` as the test command fails the reviewer immediately: `Checks` is a console executable, not a test project, so that command never runs the seven contract checks.",
            verify="In a fresh copy, run every README command in order and confirm the seven-check message and the six ApiLab statuses 200, 201, 200, 409, 400 and 404.",
        ),
    },
}

# Answers for the remaining tasks 1 to 5. Entries with `code` run in the reference
# program like the ANSWERS above; the others are written answers.
TASK_ANSWERS = {
    1: {
        1: dict(
            explain='`"Hello, C#"` has nine characters: the five letters of `Hello`, the comma, one space, `C` and `#`. Example A checks `greeting.Length == 9` before printing, so a correct prediction is 9.',
            why="`string.Length` counts UTF-16 code units, and every character in this ASCII fixture is one unit. The comma and the space are characters like any letter, so they add 2 to the 7 visible letters and symbols.",
            wrong="Counting only letters gives 6 (`Hello` plus `C`) and counting letters and symbols but not the space gives 8. Either guess, written into the check, makes the program stop with `greeting length` before anything prints.",
            verify="Run Example A unchanged: `Hello, C#` prints and the marker follows. Then change the expected value in the check to 8 and confirm the run fails with the reason `greeting length`.",
        ),
        2: dict(
            code="""string greeting = "Hi there, Ada!";
Check(greeting.Length == 14, "changed greeting length");""",
            observe="The new greeting has 14 characters and the check passes silently.",
            explain="This task starts from Example A, the greeting. The expected 14 was counted by hand before running: `Hi` (2), a space (1), `there,` (6), a space (1) and `Ada!` (4). The check compares the program's count with that independent count, not with a value copied from output.",
            wrong="Running the program, reading the length it prints and pasting that number into the check makes the check agree with whatever the code does. It can no longer catch a typo such as a doubled space in the new greeting.",
            verify="Add a second space after the comma and rerun: the program must stop with `changed greeting length`, because the text now has 15 characters. Remove the extra space and the check passes again.",
        ),
        4: dict(
            explain='Delete the semicolon after `string greeting = "Hello, C#"` and build. The compiler reports error CS1002, `; expected`, and positions it at the end of that statement, just after the closing quote. The build stops, so no program runs: nothing prints, not even the greeting. That makes it a compilation failure, not a runtime failure. Restore the semicolon and the run succeeds again.',
            why="C# requires a semicolon to end each declaration statement. The parser notices the problem only when it reaches the end of the statement without one, which is why the diagnostic points at the end of the line rather than at any earlier word. A runtime failure, by contrast, needs a compiled program that starts and then throws.",
            wrong="Treating it as a runtime crash and looking for an exception or a stack trace finds nothing, because no executable was produced. Searching the next line for the mistake is also misleading: the error belongs to the statement that ends where the diagnostic points.",
            verify="With the semicolon removed, confirm the build output contains `CS1002` with the line of the greeting declaration and that the run produces no `Hello, C#` and no lesson marker. Put the semicolon back and confirm both lines print.",
        ),
        5: dict(
            code="""int seatsPerRow = 6;
int noRows = 0 * seatsPerRow;
int oneRow = 1 * seatsPerRow;
Check(noRows == 0, "zero rows hold no seats");
Check(oneRow == seatsPerRow, "one row holds one row of seats");""",
            observe="Zero rows give 0 seats and one row gives 6 seats, both from the same formula.",
            explain="Zero times any count is zero and one times a count is that count, so `rows * seatsPerRow` is already correct at both edges. No `if (rows == 0)` branch is needed, and the formula from task 3 needs no special case for small halls.",
            wrong="Adding `if (rows == 0) seats = 0; else seats = rows * seatsPerRow;` produces the same numbers with an extra path that must be tested and maintained. Worse, a special case written as `seats = 1` for an empty hall would quietly disagree with the formula.",
            verify="Also check two rows: `2 * seatsPerRow` must be 12. If the three results 0, 6 and 12 grow by the same step, the formula is linear in rows, as the seat plan expects.",
        ),
    },
    2: {
        1: dict(
            explain="`7/2` is an `int` with value 3. `7/2.0` is a `double` with value 3.5. `(double)(7/2)` is a `double` with value 3.0: the parentheses force the integer division first, and the cast converts the already truncated 3.",
            why="The operand types choose the operator. Two `int` operands select integer division, which discards the remainder. One `double` operand promotes the other, so division keeps the fraction. A cast applies to the expression it is written on, so its position decides whether it runs before or after the truncation.",
            wrong="Expecting `(double)(7/2)` to give 3.5 assumes the cast reaches inside the parentheses. It does not: the cast receives the integer 3, and converting 3 to `double` cannot bring back the missing half.",
            verify="Add `Check(7 / 2 == 3, ...)`, `Check(7 / 2.0 == 3.5, ...)` and `Check((double)(7 / 2) == 3.0, ...)` to Example A. Hovering each expression in an editor also shows its static type.",
        ),
        2: dict(
            code="""int whole = 8 / 2;
double fraction = (double)8 / 2;
Check(whole == 4 && fraction == 4.0, "even operands agree");
Check(7 / 2 != (double)7 / 2, "odd operands expose truncation");""",
            observe="With 8 and 2 both divisions give 4, while 7 and 2 still give 3 and 3.5.",
            explain="8 is an exact multiple of 2, so the remainder that integer division throws away is 0. Both kinds of division therefore produce 4, and a test using only these inputs cannot tell correct code from code that truncates. The second check keeps the odd case that exposes the difference.",
            wrong="Replacing the lesson's test data with 8 and 2 and seeing all checks pass suggests the conversion is right. The same passing run would appear for `(double)(a / b)`, which is wrong for every odd numerator.",
            verify="Change the operands to 9 and 2: `whole` must become 4 and `fraction` 4.5, and the first check now fails, showing that only remainder-producing inputs reveal truncation.",
        ),
        4: dict(
            explain="In `double average = (double)(total / count);` with `total = 7` and `count = 2`, the division runs on two `int` values and yields 3, and the cast then produces 3.0. The correct average is 3.5. Fix it by converting an operand before dividing: `double average = (double)total / count;`.",
            why="The cast in the faulty line is applied to the result of `total / count`, after the fraction is gone. Casting `total` first makes the division a `double` division, so the remainder survives as `.5`.",
            wrong="Testing with `total = 6` and `count = 2` gives 3.0 from both versions, so the bug passes. A fractional counterexample needs a total that the count does not divide, such as 7 and 2.",
            verify="Check `(double)(7 / 2) == 3.0` to reproduce the bug and `(double)7 / 2 == 3.5` for the fix. Then try `total = 1`, `count = 3` and confirm the fixed version gives about 0.333, not 0.",
        ),
        5: dict(
            code="""bool TryCount(string text, out int count) {
  var style = NumberStyles.Integer;
  var culture = CultureInfo.InvariantCulture;
  bool parsed = int.TryParse(text, style, culture, out count);
  return parsed && count >= 0;
}
Check(!TryCount("", out _), "empty text rejected");
Check(TryCount("0", out int zero) && zero == 0, "zero accepted");
Check(!TryCount("-5", out _), "negative rejected");
Check(!TryCount("2147483648", out _), "beyond int range rejected");
Check(TryCount("2147483647", out int max) && max == int.MaxValue,
      "largest int accepted");""",
            observe="Empty text, -5 and 2147483648 are rejected; 0 and 2147483647 are accepted.",
            explain='Each input tests a different rule. `""` has no digits, so `TryParse` fails. `"0"` is the smallest valid quantity. `"-5"` parses, so the separate `count >= 0` test must reject it. `"2147483648"` is `int.MaxValue + 1`, so `TryParse` reports failure instead of wrapping, while `"2147483647"` sits exactly on the boundary and is accepted.',
            wrong="Checking only that `TryParse` returned true accepts `-5` as a quantity. Using `int.Parse` instead turns the empty and oversized inputs into `FormatException` and `OverflowException`, which a caller has to catch separately.",
            verify='Add `TryCount(" 7", out _)` and decide the policy: `NumberStyles.Integer` allows surrounding spaces, so it is accepted. If quantities must be bare digits, switch to `NumberStyles.None` and confirm the check flips.',
        ),
    },
    3: {
        1: dict(
            explain="`checked(large + 1)` throws `OverflowException`; `checked(100 + 20)` returns 120. `int` is a 32-bit two's complement type whose largest value is `int.MaxValue`, 2147483647. Adding 1 needs a value the 32 bits cannot represent, and `checked` turns that into an exception instead of a wrapped result.",
            why="The range of `int` runs from -2147483648 to 2147483647. 120 is far inside it. `large + 1` would be 2147483648, one past the top, and without `checked` the bits would wrap to `int.MinValue`, a negative count.",
            wrong="Predicting that both lines succeed because 2147483648 looks like an ordinary number ignores the fixed width of `int`. Predicting that the program crashes at compile time is also wrong: `large` is a variable, so the overflow is found while running.",
            verify='Run Example A: the `overflow must be visible` check passes, proving the exception was caught. Then add `Check(unchecked(int.MaxValue + 1) == int.MinValue, "wraps")` to see the silent result that `checked` prevents.',
        ),
        2: dict(
            code="""bool overflowed = false;
try {
  int small = int.MinValue;
  _ = checked(small - 1);
} catch (OverflowException) {
  overflowed = true;
}
Check(overflowed, "minimum minus one rejected");
Check(checked(-100 - 20) == -120, "normal subtraction");""",
            observe="int.MinValue minus one throws OverflowException; -100 minus 20 returns -120.",
            explain="The lower boundary behaves like the upper one. `int.MinValue` is -2147483648, and -2147483649 does not fit in 32 bits, so the checked subtraction throws. A value well inside the range still subtracts normally, which shows the check rejects only the boundary crossing.",
            wrong="Assuming the failure cannot happen at the bottom of the range because counts are usually positive leaves differences such as `start - end` unprotected. Without `checked`, `int.MinValue - 1` silently becomes `int.MaxValue`.",
            verify="Remove `checked` from the subtraction (wrap it in `unchecked(...)`) and confirm `overflowed` stays false and the result equals `int.MaxValue`. Restore `checked` and the first check passes again.",
        ),
        4: dict(
            explain='Parsing `"2.675"` with `double.Parse` stores the nearest binary fraction, 2.67499999999999982236431605997495353221893310546875. The approximation enters at that parse, before any decimal exists. Code that rounds or computes while the value is still a `double` sees a number below the midpoint: `Math.Round(2.675, 2, MidpointRounding.AwayFromZero)` gives 2.67. Parse money with `decimal.Parse(text, CultureInfo.InvariantCulture)`, which keeps 2.675 exactly and rounds it to 2.68.',
            why="`double` stores base-2 fractions, and 0.675 has no finite base-2 form. `decimal` stores a base-10 integer and a scale, so 2.675 is exactly 2675 with scale 3. A later `(decimal)` conversion cannot know which decimal text produced the binary value.",
            wrong="Converting to `decimal` immediately after the `double` parse and assuming that repairs the value hides the problem in simple cases, because the conversion rounds to about 15 significant digits. Any `double` arithmetic or rounding done before the conversion still used the approximate value.",
            verify="Check `Math.Round(2.675, 2, MidpointRounding.AwayFromZero) == 2.67` and `Math.Round(2.675m, 2, MidpointRounding.AwayFromZero) == 2.68m`. The two policies differ only because of where the approximation entered.",
        ),
        5: dict(
            code="""var even = MidpointRounding.ToEven;
var away = MidpointRounding.AwayFromZero;
Check(Math.Round(2.344m, 2, even) == 2.34m, "below, even");
Check(Math.Round(2.344m, 2, away) == 2.34m, "below, away");
Check(Math.Round(2.345m, 2, even) == 2.34m, "midpoint, even");
Check(Math.Round(2.345m, 2, away) == 2.35m, "midpoint, away");
Check(Math.Round(2.346m, 2, even) == 2.35m, "above, even");
Check(Math.Round(2.346m, 2, away) == 2.35m, "above, away");""",
            observe="2.344 rounds to 2.34 and 2.346 to 2.35 under both policies; only 2.345 differs, 2.34 versus 2.35.",
            explain="A midpoint policy applies only to values exactly halfway between two candidates. 2.344 is nearer 2.34 and 2.346 is nearer 2.35, so both policies agree. At 2.345 `ToEven` picks the candidate with an even last digit, 2.34, while `AwayFromZero` picks 2.35. Decimal literals keep these thousandths exact, so the midpoint is a real midpoint.",
            wrong="Testing only 2.345 shows the policies differ but cannot show that they agree elsewhere. Testing only 2.344 and 2.346 makes the policy choice look irrelevant, and a later switch of policy would pass unnoticed.",
            verify="Add 2.355m: `ToEven` gives 2.36 because 6 is even, and `AwayFromZero` also gives 2.36. Then add -2.345m and confirm `AwayFromZero` gives -2.35, away from zero rather than upward.",
        ),
    },
    4: {
        1: dict(
            explain='After the call, `original` is still `"data"` and `changed` is `"DATA"`. `ToUpperInvariant` does not alter the string it is called on; it builds and returns a new string object, and the caller owns that result through `changed`.',
            why="`string` is immutable in .NET: no method can change the characters of an existing instance. Every transforming method such as `ToUpperInvariant`, `Trim` or `Replace` returns a new instance, and the original variable keeps referring to the original object.",
            wrong='Predicting that both variables now hold `"DATA"` treats the call as in-place mutation. Code built on that idea, such as calling `name.ToUpperInvariant();` on its own line, discards the result and leaves `name` unchanged.',
            verify='Example A already checks `original == "data" && changed == "DATA"`. Add `Check(!ReferenceEquals(original, changed), "new object")` to confirm the result is a separate string.',
        ),
        2: dict(
            code="""string Label(int count) {
  string unit = count == 1 ? "file" : "files";
  return $"{count} {unit}";
}
Check(Label(3) == "3 files", "plural label");
Check(Label(1) == "1 file", "singular label");
Check(Label(0) == "0 files", "zero uses the plural");""",
            observe="The labels are 3 files, 1 file and 0 files.",
            explain='The interpolated string `$"{count} {unit}"` formats the number and inserts the unit chosen just before it. Choosing the unit in a separate line keeps the grammar rule visible and testable, and checking 1 and 0 covers the two counts where English plurals usually go wrong.',
            wrong='Writing `$"{count} file(s)"` avoids the decision and produces `1 file(s)` for every count. Hardcoding `"files"` instead produces the incorrect `1 files`.',
            verify="Call `Label(1000)` and check the result is `1000 files`: `int` formatting adds no group separator by default. If a display needs `1,000`, format with an explicit culture and test that string separately.",
        ),
        4: dict(
            explain='`char first = symbol[0];` for `symbol = "😀"` yields `\\uD83D`, the high surrogate of the pair that encodes U+1F600. It is half of a symbol: printed or encoded on its own it becomes the replacement character, not a smiley. Take a whole scalar with `Rune.GetRuneAt(symbol, 0)` or `symbol.EnumerateRunes().First()`, whose value is 0x1F600.',
            why="A `char` is one UTF-16 code unit. Code points above U+FFFF need two units, a high surrogate followed by a low surrogate, which is why Example B reports `Length == 2`. Indexing returns a single unit, so it cannot represent the emoji.",
            wrong="Using `symbol.Substring(0, 1)` instead of indexing has the same flaw, because it also counts UTF-16 units. Truncating display names with `name[..20]` can likewise cut through an emoji and leave a broken surrogate at the end.",
            verify='Check `char.IsHighSurrogate(symbol[0])` is true and `Rune.GetRuneAt(symbol, 0).Value == 0x1F600`. Also check `Encoding.UTF8.GetString(Encoding.UTF8.GetBytes(symbol[0].ToString())) == "\\uFFFD"` to see the damaged half.',
        ),
        5: dict(
            code="""string ascii = "A";
string emoji = "\\U0001F600";
string accented = "e\\u0301";
int Elements(string text) => new StringInfo(text).LengthInTextElements;
Check(ascii.Length == 1 && Elements(ascii) == 1, "ASCII");
Check(emoji.Length == 2 && Elements(emoji) == 1, "emoji");
Check(accented.Length == 2 && Elements(accented) == 1, "combining mark");
Check(accented.EnumerateRunes().Count() == 2, "two scalars");""",
            observe="Each input is one text element, but the emoji and the accented e each use two UTF-16 code units.",
            explain="`A` is one code unit and one text element. The emoji is one scalar stored as two code units. `e` followed by U+0301 COMBINING ACUTE ACCENT is two scalars and two code units that a reader sees as one character, so `StringInfo.LengthInTextElements` reports 1 for all three while `Length` reports 1, 2 and 2.",
            wrong="Counting runes instead of code units fixes the emoji but not the accent: `EnumerateRunes` still sees two scalars in `e\\u0301`. Only text elements match what a reader counts as characters.",
            verify="Normalize the accented string with `accented.Normalize(NormalizationForm.FormC)` and check its `Length` becomes 1, because the precomposed é exists. A flag emoji such as U+1F1FA U+1F1F8 shows the opposite: four code units, two runes and one text element.",
        ),
    },
    6: {
        1: dict(
            explain="Before the loop `sum` is 0. After visiting 2 it is 2, after 4 it is 6, and after 6 it is 12. At every point `sum` equals the total of the elements visited so far: 0 for none, then 2, 2 + 4 and 2 + 4 + 6.",
            why="The loop body adds exactly the current element and nothing else, so if the invariant holds before an iteration it holds after it. It holds at the start because the total of no elements is 0, and when the loop ends every element has been visited, so `sum` is the full total.",
            wrong="Starting the trace at 2 skips the state before the first iteration, which is the state that explains why an empty array correctly sums to 0. Writing 12 after the first step confuses the final result with an intermediate value.",
            verify='Insert `Console.WriteLine($"{value} -> {sum}");` after `sum += value;` and confirm the lines `2 -> 2`, `4 -> 6` and `6 -> 12`. Remove the line afterwards so the lesson output is unchanged.',
        ),
        2: dict(
            code="""int[] values = { 2, -3, 4, -1, 6 };
int sum = 0;
foreach (int value in values) {
  if (value < 0)
    continue;
  sum += value;
}
Check(sum == 12, "negatives skipped");
Check(sum == values.Where(v => v >= 0).Sum(), "same as filtered sum");""",
            observe="The sum is 12: the -3 and -1 are skipped and 2, 4 and 6 are added.",
            explain="The invariant becomes: `sum` equals the total of the nonnegative elements visited so far. `continue` leaves `sum` untouched for a negative value, so the invariant still holds after that iteration, and the final sum matches a separately computed filtered sum.",
            wrong="Writing `sum += Math.Max(value, 0)` gives the same total here but hides the policy inside arithmetic. Writing `if (value < 0) break;` stops at -3 and returns 2, silently dropping every later value.",
            verify="Make every value negative and check that `sum` is 0, the same identity as the empty array. Then put a 0 in the array and confirm it is kept, because the rule skips only values below zero.",
        ),
        4: dict(
            explain="With `values = { 5 }` the loop `for (int i = 0; i <= values.Length; i++)` runs for `i = 0` and reads 5, then tests `1 <= 1`, which is true, and reads `values[1]`. That index does not exist, so the program throws `IndexOutOfRangeException`. The bound must be `i < values.Length`.",
            why="A one-element array has length 1 and only index 0. Valid indices run from 0 to `Length - 1`, so the loop must stop when `i` reaches `Length`. With `<=` the loop always makes one extra iteration.",
            wrong="Catching `IndexOutOfRangeException` around the loop hides the off-by-one error while still doing the extra iteration. Changing the start to `i = 1` avoids the crash for this input but skips the first element.",
            verify="Run the `<=` version with `{ 5 }` and observe the exception. With `<`, check that a search for 5 returns index 0 and that the loop body runs exactly once.",
        ),
        5: dict(
            code="""int FirstIndex(int[] items, int target) {
  for (int i = 0; i < items.Length; i++) {
    if (items[i] == target)
      return i;
  }
  return -1;
}
int[] empty = Array.Empty<int>();
int[] single = { 4 };
int[] other = { 1, 2 };
int[] repeated = { 4, 9, 4 };
Check(FirstIndex(empty, 4) == -1, "empty input");
Check(FirstIndex(single, 4) == 0, "singleton match");
Check(FirstIndex(other, 4) == -1, "no match");
Check(FirstIndex(repeated, 4) == 0, "repeated match returns the first");""",
            observe="The empty and no-match inputs give -1; the singleton and the repeated input give index 0.",
            explain="Each input guards a different mistake. The empty array checks that the loop body may run zero times. The singleton checks the first and last index at once. The no-match array checks that the loop ends without inventing a result. The repeated array checks that the search stops at the first 4 instead of reporting index 2.",
            wrong="Testing only `{ 3, 8, 8 }` as in Example B never runs the loop zero times and never reaches the final `return -1`, so a version that returns 0 when nothing matches would pass it while pointing callers at a real element.",
            verify="Change `return i;` to remember `i` and continue the loop; the repeated check must then fail with index 2. Restore the early return and all four checks pass.",
        ),
    },
    7: {
        1: dict(
            explain="The caller evaluates `original`, which is 7, and passes a copy to `Double`. Inside, the parameter `value` is 7 and the method returns `checked(7 * 2)`, which is 14. That return value is assigned to `result`. `original` is still 7, because the method only received a copy. `Double(0)` binds `value` to 0 and returns 0.",
            why="`int` is a value type and the parameter is not `ref` or `out`, so passing it copies the value. Assigning to `value` inside the method could not affect `original`, and the method communicates only through its return value.",
            wrong="Expecting `original` to become 14 treats the call as if it modified its argument in place. That would require a `ref int` parameter, and the call would have to say `ref` explicitly.",
            verify="Example A already checks `result == 14 && original == 7`. Add a line inside `Double` that assigns `value = 100` before returning and confirm `original` is still 7.",
        ),
        2: dict(
            code="""int Triple(int value) => checked(value * 3);
Check(Triple(0) == 0, "zero stays zero");
Check(Triple(-4) == -12, "negative input keeps its sign");
Check(Triple(5) == 15, "positive input");""",
            observe="Triple returns 0 for 0, -12 for -4 and 15 for 5.",
            explain="Multiplying by 3 maps 0 to itself and keeps the sign of other inputs, so the expected values can be worked out independently: 0, -12 and 15. `checked` matches `Double`, so an input above `int.MaxValue / 3` throws instead of wrapping.",
            wrong="Implementing `Triple` as `value + value + value` passes these checks but skips `checked` unless it is added, so `Triple(int.MaxValue)` would wrap silently. Testing only 5 cannot tell a correct `Triple` from `value + 10`.",
            verify="Add a check that `Triple(1_000_000_000)` throws `OverflowException`, since 3 billion is above `int.MaxValue`, and that `Triple(-715_827_882) == -2_147_483_646` still fits.",
        ),
        4: dict(
            explain="`int DivideExactly(int value, int divisor) => value / divisor;` returns 3 for `DivideExactly(7, 2)`. The name promises an exact quotient, but integer division drops the remainder 1, so every caller receives a value that is not exact and no error tells them. Either enforce the promise with `if (value % divisor != 0) throw new ArgumentException(...)`, as Example B does, or rename the method `DivideTruncating`.",
            why="The method name is part of the contract a caller reads. When the body does something weaker than the name says, the mismatch spreads into every call site, and the remainder test makes the hidden case explicit.",
            wrong="Returning 0 or -1 for non-divisible input creates a sentinel that looks like a valid quotient, the pattern the pitfalls warn about. Changing the return type to `double` changes what the method does without changing its misleading name.",
            verify="Check that the faulty version returns 3 for `(7, 2)`. With the fix, check that `(12, 3)` still returns 4 and `(7, 2)` throws `ArgumentException`.",
        ),
        5: dict(
            code="""int DivideExact(int value, int divisor) {
  if (divisor == 0)
    throw new DivideByZeroException();
  if (value % divisor != 0)
    throw new ArgumentException("not an exact quotient");
  return value / divisor;
}
bool zeroRejected = false;
try {
  DivideExact(6, 0);
} catch (DivideByZeroException) {
  zeroRejected = true;
}
bool remainderRejected = false;
try {
  DivideExact(7, 2);
} catch (ArgumentException) {
  remainderRejected = true;
}
Check(zeroRejected, "zero divisor has its own failure");
Check(remainderRejected, "remainder has its own failure");
Check(DivideExact(-12, 3) == -4, "exact negative quotient");""",
            observe="A zero divisor throws DivideByZeroException, 7 by 2 throws ArgumentException and -12 by 3 returns -4.",
            explain="The two failures have different causes, so each gets its own exception and its own test. The zero test runs first because `value % 0` would itself throw before the remainder test could explain anything. Testing them separately proves that each guard works on its own instead of one catch block hiding which rule fired.",
            wrong="Putting both calls in one `try` block and catching `Exception` stops at the first throw, so the `(7, 2)` call never runs and a missing remainder guard goes unnoticed.",
            verify="Delete the remainder guard and confirm the second check fails because `DivideExact(7, 2)` returns 3. Deleting the zero guard instead still passes, since `6 % 0` throws the same exception type; compare the exception messages to see which line raised it.",
        ),
    },
    12: {
        1: dict(
            explain="Example A: `first` holds the struct value X 2, Y 3. `var second = first;` copies both fields into a second value, so there are two independent points. `second.X = 9` changes only the copy: `first` is (2, 3) and `second` is (9, 3). Example B: `first` holds a reference to one `Counter` object with `Value` 0. `var second = first;` copies the reference, not the object, so both variables point at the same counter. `second.Value++` changes that object to 1, and `first.Value` reads the same 1.",
            why="`Point` is a struct, so a variable of that type contains the data itself and assignment duplicates it. `Counter` is a class, so a variable contains a reference, and assignment duplicates only the reference. The drawing needs two boxes for A and one shared box with two arrows for B.",
            wrong="Drawing B like A, with two counters, predicts `first.Value == 0` and makes `ReferenceEquals(first, second)` look impossible. Drawing A like B predicts that `first.X` becomes 9.",
            verify="Both examples already check the result. Add `Check(!ReferenceEquals(second, new Counter()), ...)` in B and print `first.Y` and `second.Y` in A to confirm that the untouched field 3 was copied too.",
        ),
        2: dict(
            code="""var first = new Counter();
first.Value = 5;
var second = new Counter();
second.Value = 5;
Check(first.Value == second.Value, "equal property values");
Check(!ReferenceEquals(first, second), "separate identities");
Check(!first.Equals(second), "class Equals defaults to identity");
second.Value++;
Check(first.Value == 5 && second.Value == 6, "independent state");""",
            observe="Two counters both hold 5 but are different objects; incrementing one leaves the other at 5.",
            explain="`new Counter()` runs twice, so there are two objects. Their `Value` properties are equal, but `ReferenceEquals` asks whether the variables point at the same object, and they do not. `Counter` does not override `Equals`, so it inherits reference equality from `object` and also reports false. Because the objects are separate, the increment changes only `second`.",
            wrong="Using `first.Equals(second)` as the test for equal content gives false here and suggests the values differ. For a class without an override, `Equals` answers the identity question, not the content question.",
            verify="Replace `var second = new Counter();` with `var second = first;` and confirm the identity check now fails and the increment makes `first.Value` 6. Restore the second `new` afterwards.",
        ),
        4: dict(
            explain="`var backup = session; session.Value = 10;` leaves `backup.Value` at 10 as well, because `backup` is a second reference to the same `Counter`. Assigning a class variable never copies the object. To keep an independent snapshot, create a new object: `var backup = new Counter(); backup.Value = session.Value;`, or give the class an explicit copy method.",
            why="A class variable stores a reference. Assignment copies that reference, so both names lead to one object and every mutation through either name is visible through the other. Only a constructor call or a copy method produces a second object.",
            wrong="Switching `Counter` to a struct to get copying changes the meaning of every other use, including the shared-session behavior Example B relies on. A shallow copy is also not enough when the class holds a mutable list, because the copy would share that list.",
            verify="Check `ReferenceEquals(backup, session)` is true for the faulty version and that `backup.Value` follows the change to 10. With the explicit copy, check `!ReferenceEquals(backup, session)` and that `backup.Value` keeps its old value.",
        ),
        5: dict(
            code="""var original = (Count: 1, Items: new List<int> { 1 });
var copy = original;
copy.Count = 2;
copy.Items.Add(2);
Check(original.Count == 1, "value field copied");
Check(original.Items.Count == 2, "list content shared");
Check(ReferenceEquals(original.Items, copy.Items), "same list object");""",
            observe="The copied tuple changes its own Count to 2, but original.Items also contains two elements after the Add.",
            explain="A value tuple is a struct, so assignment copies its fields. `Count` is an `int`, and its copy is independent. `Items` is a reference to a `List<int>`, and copying it copies the reference, so both tuples point at one list. Adding through `copy.Items` therefore changes the list that `original.Items` sees.",
            wrong="Assuming that struct semantics make the whole value immutable from the outside predicts `original.Items.Count == 1`. Value semantics apply only one level deep: the reference is copied, the list it refers to is not.",
            verify="Give the copy its own list with `copy.Items = new List<int>(original.Items);` before the `Add` and confirm `original.Items.Count` stays 1 and `ReferenceEquals` becomes false.",
        ),
    },
    16: {
        1: dict(
            explain='Example B: `"pear,2"` splits into two fields, the name is not blank, `2` parses and is not negative, so `pear` goes from 0 to 2. `"pear,no"` has two fields but `no` fails `TryParse`, so `Rejected` becomes 1. `"apple,-1"` parses to -1, which fails `quantity < 0`, so `Rejected` becomes 2 and `apple` is never added. `"broken"` splits into one field, so the field-count test rejects it before any index is read and `Rejected` becomes 3. The result is one entry, `pear` 2, and 3 rejections.',
            why="Every line passes through the same ordered tests: field count, name, number, sign. A line contributes to `Counts` only if it passes all four, and every failed line increments `Rejected` exactly once because of the `continue`.",
            wrong="Assuming `apple,-1` creates an `apple` entry with 0 misses that the sign test runs before the dictionary update. Assuming `broken` throws `IndexOutOfRangeException` misses that the field count is checked before `fields[1]` is read.",
            verify='Example B checks `Rejected == 3` and `Counts.Count == 1`. Add `Check(!totals.Counts.ContainsKey("apple"), ...)` to confirm the rejected apple line left no entry.',
        ),
        2: dict(
            code="""var totals = Import(new[] { "pear,2", "apple,3", "pear,4", "apple,5" });
Check(totals.Rejected == 0, "duplicate line accepted");
Check(totals.Counts["apple"] == 8, "predicted apple total");
Check(totals.Counts["pear"] == 6, "pear unchanged");
Check(totals.Counts.Count == 2, "no new key");""",
            observe="The added apple,5 is accepted: apple becomes 8, pear stays 6 and there are still two keys.",
            explain="The prediction written before running was 3 + 5 = 8 for apple, with pear and the key count unchanged. `Import` reads the existing total with `TryGetValue` and adds the new quantity, so a repeated valid name accumulates instead of replacing or being rejected.",
            wrong="Predicting apple 5 assumes the later line overwrites the earlier one, which is what `counts[name] = quantity` would do. Predicting a rejection treats a repeated name as a duplicate-key error, which is a policy this importer does not have.",
            verify='Add `"Apple,1"` and confirm it creates a third key, because the dictionary uses `StringComparer.Ordinal`. That shows the case policy the pitfalls say must be documented.',
        ),
        4: dict(
            explain='`int.TryParse(fields[1], out int quantity); counts[name] = before + quantity;` ignores the returned bool. For `"pear,no"` the parse fails, `quantity` is set to 0, and the importer inserts `pear` with 0 and counts no rejection. Bad data now looks like a real zero-quantity line. The fix is to branch on the result, as `Import` does: `if (!int.TryParse(...)) { rejected++; continue; }`.',
            why='`TryParse` reports failure only through its return value; the `out` value is always assigned and is 0 on failure. Discarding the bool removes the only signal that separates `"pear,0"` from `"pear,no"`.',
            wrong='Checking afterwards with `if (quantity == 0) rejected++` rejects the legitimate `"pear,0"` too, and still lets nothing distinguish a typo from a real zero.',
            verify='Import `"pear,no"` with the faulty version and observe `Counts["pear"] == 0` and `Rejected == 0`. With the real `Import`, check `Counts.Count == 0` and `Rejected == 1`.',
        ),
        5: dict(
            code="""var blank = Import(new[] { ",3", "  ,3" });
Check(blank.Rejected == 2, "empty and blank names rejected");
Check(blank.Counts.Count == 0, "no entry for a blank name");
var extra = Import(new[] { "pear,2,box" });
Check(extra.Rejected == 1, "extra field rejected");
var zero = Import(new[] { "pear,0" });
Check(zero.Rejected == 0 && zero.Counts["pear"] == 0, "zero accepted");
var none = Import(Array.Empty<string>());
Check(none.Rejected == 0 && none.Counts.Count == 0, "empty input");""",
            observe="Blank names and the extra field are rejected, pear,0 is accepted with total 0 and empty input gives no counts and no rejections.",
            explain='`",3"` and `"  ,3"` reach `IsNullOrWhiteSpace` and fail it. `"pear,2,box"` splits into three fields and fails the length test, so `2` is never parsed. `"pear,0"` passes every test because the rule rejects only negative quantities, so it records a real zero. No lines means no iterations, and both outputs keep their starting values.',
            wrong="Treating zero as invalid because it adds nothing would make `pear,0` a rejection and lose the evidence that pear was reported. Accepting `pear,2,box` by reading only the first two fields would hide a format change in the source file.",
            verify='Add `"pear, 2"` with a space before the number and decide: `int.TryParse` allows leading whitespace, so it is accepted as 2. If the contract forbids spaces, tighten the parse and confirm the check flips.',
        ),
    },
    19: {
        1: dict(
            explain="The first call `scale(3)` returns 6 because `factor` is 2. After `factor = 4`, the same delegate returns 12. The lambda captured the variable `factor`, not its value at the time the lambda was created.",
            why="The compiler moves a captured local into a hidden object shared by the method and the lambda. Assigning `factor = 4` writes to that shared storage, and the next call reads it.",
            wrong="Predicting 6 for both calls treats capture as a copy taken at creation time. That is how a parameter or a separate local snapshot behaves, not a captured variable.",
            verify="Example A checks both values. Insert `factor = 10;` before the second check and confirm `scale(3)` would now be 30, which shows the delegate reads the variable at each call.",
        ),
        2: dict(
            code="""int factor = 2;
int snapshot = factor;
Func<int, int> live = value => value * factor;
Func<int, int> frozen = value => value * snapshot;
factor = 4;
Check(live(3) == 12, "live capture sees the new factor");
Check(frozen(3) == 6, "snapshot keeps the old factor");""",
            observe="After factor changes to 4, live(3) is 12 while frozen(3) is still 6.",
            explain="`snapshot` is a separate local that received the value 2 once. The `frozen` lambda captures `snapshot`, and nothing assigns to it later, so its result stays 6. The `live` lambda captures `factor`, which changed, so its result follows to 12.",
            wrong="Writing `Func<int, int> frozen = value => value * factor;` and expecting it to remember 2 because it was created earlier gives 12 instead. The creation time of a lambda does not freeze the variables it reads.",
            verify="Assign `snapshot = 5;` after creating `frozen` and confirm `frozen(3)` becomes 15. The snapshot is only safe while nothing writes to it.",
        ),
        4: dict(
            explain="`source.Raised += (_, _) => calls++;` followed by `source.Raised -= (_, _) => calls++;` does not unsubscribe. The second lambda creates a new delegate instance that is not equal to the subscribed one, so the removal finds no match and silently does nothing. After two `Emit` calls `calls` is 2. Keep the delegate in a variable, as Example B does with `handler`, and remove that same variable.",
            why="Event removal compares delegates by target and method. Each lambda expression that captures `calls` produces its own delegate, so two textually identical lambdas do not compare equal, and `-=` removes nothing.",
            wrong="Assuming the removal worked because no exception was raised misreads the API: removing a delegate that is not subscribed is allowed and has no effect. The leftover handler keeps the subscriber and everything it captured alive.",
            verify="Run the faulty version: emit, remove with a new lambda, emit again, and check `calls == 2`. With the stored `handler`, the same sequence gives `calls == 1`, as Example B shows.",
        ),
        5: dict(
            code="""var source = new Signal();
int first = 0;
int second = 0;
source.Emit();
Check(first == 0 && second == 0, "no subscribers, no calls");
source.Raised += (_, _) => first++;
source.Raised += (_, _) => second++;
source.Emit();
Check(first == 1 && second == 1, "both subscribers called once");""",
            observe="Emitting with no subscribers does nothing and does not throw; with two subscribers each counter becomes 1.",
            explain="With no subscribers `Raised` is null, and `Raised?.Invoke(...)` skips the call instead of throwing `NullReferenceException`. Each `+=` adds a delegate to the invocation list, so one `Emit` calls both handlers once, in subscription order.",
            wrong="Writing `Raised.Invoke(this, EventArgs.Empty)` without `?.` passes the two-subscriber test but throws on the first `Emit` with no subscribers. Testing only the two-subscriber case would never reveal it.",
            verify="Subscribe the same delegate twice and confirm one `Emit` increments it twice. Then remove it once and confirm the next `Emit` increments it once.",
        ),
    },
    21: {
        1: dict(
            explain="Example A: the input grain is one row per sale event (`Kind`, `Amount`); the output grain is one row per kind, two totals from three events. Example B: `left` has one row per key and `right` has one row per value event for a key; the joined output has one row per matching left-right pair, so one left row with two matches becomes two rows.",
            why="Grain is what one row represents. `GroupBy` with `Sum` deliberately coarsens the grain to the grouping key. `Join` produces the product of matches per key, so its output grain is a pair, and it is finer than the left input whenever the right side repeats a key.",
            wrong="Describing B's output as one row per key assumes `Join` behaves like a lookup. That expectation is what leads to doubled totals when the right side has repeated keys.",
            verify="Check `rows.Length == 3` and `totals.Count == 2` in A, and `left.Length == 1` and `joined.Length == 2` in B. Each count is the number of rows at that grain.",
        ),
        2: dict(
            code="""var rows = new List<(string Kind, int Amount)> { ("a", 2), ("a", 3) };
rows.Add(("b", 4));
rows.Add(("c", 7));
var groups = rows.GroupBy(row => row.Kind);
var totals = groups.ToDictionary(g => g.Key, g => g.Sum(r => r.Amount));
Check(totals.Count == 3 && totals["c"] == 7, "third category");
int eventTotal = rows.Sum(row => row.Amount);
Check(eventTotal == 16, "independent event total");
Check(totals.Values.Sum() == eventTotal, "total conserved");""",
            observe="Category c appears with 7, and the three category totals add up to 16, the same as the four events.",
            explain="Grouping reassigns each event to exactly one category and summing adds every amount once, so the grand total must not change: 5 + 4 + 7 = 2 + 3 + 4 + 7 = 16. Checking that conservation catches lost or duplicated rows that a per-category check alone could miss.",
            wrong='Checking only `totals["c"] == 7` confirms the new category but not that the others survived. A filter that accidentally dropped kind `b` would still pass it.',
            verify='Add an event with kind `a` and amount 1 and confirm `totals["a"]` becomes 6, the count stays 3 and both sides of the conservation check become 17.',
        ),
        4: dict(
            explain='If the item metadata contains `(Id: 1, Name: "pear")` twice, joining sales with Qty 2 and 3 for id 1 to it yields four rows instead of two, and the pear total becomes 10 instead of 5. The sales were not doubled; the metadata key was not unique, so every sale matched twice. Check uniqueness before joining, for example by building `items.ToDictionary(item => item.Id)`, which throws `ArgumentException` on the repeated id.',
            why="A join returns one row per matching pair. With 2 sales and 2 metadata rows for the same id, there are 2 times 2 pairs, and summing over them counts each sale twice. Item metadata is supposed to have one row per id, and that assumption must be enforced, not hoped for.",
            wrong="Calling `Distinct()` on the joined rows hides this example only when the duplicate rows are identical, and also deletes legitimate repeated sales with the same quantity. Dividing the total by 2 fixes one key and breaks every key that was not duplicated.",
            verify="Reproduce the bug and check the pear total is 10. Then check `items.GroupBy(i => i.Id).All(g => g.Count() == 1)` is false for the bad metadata and true after removing the duplicate, when the total returns to 5.",
        ),
        5: dict(
            code="""var names = new Dictionary<int, string>();
names.Add(1, "pear");
names.Add(2, "apple");
var sales = new[] { (Id: 1, Qty: 2), (Id: 3, Qty: 5) };
var matched = sales.Where(s => names.ContainsKey(s.Id)).ToArray();
var unmatched = sales.Where(s => !names.ContainsKey(s.Id)).ToArray();
Check(matched.Length == 1 && names[matched[0].Id] == "pear", "match");
Check(unmatched.Length == 1 && unmatched[0].Qty == 5, "reported");
int reported = matched.Sum(s => s.Qty) + unmatched.Sum(s => s.Qty);
Check(reported == sales.Sum(s => s.Qty), "nothing silently dropped");""",
            observe="Sale id 3 has no metadata; it is kept in a separate unmatched list with quantity 5, and matched plus unmatched still total 7.",
            explain="The chosen policy is to report unmatched rows rather than drop or invent them. Splitting the sales into matched and unmatched makes the missing metadata visible, and the final check proves the split loses nothing. An inner `Join` would quietly drop the 5, and looking up `names[3]` would throw `KeyNotFoundException`.",
            wrong='Substituting a label such as `"unknown"` inside the report merges every unmatched id into one line, so the reader cannot tell which metadata is missing. Silently using an inner join makes the report total 2 while the sales say 7.',
            verify='Add `names.Add(3, "plum");` and confirm `unmatched` becomes empty and `matched` has both sales. The conservation check holds either way.',
        ),
    },
    23: {
        1: dict(
            explain='In Example A, `catch (FormatException)` handles malformed numeric text: `int.Parse("oops")` cannot read digits. It does not handle the negative case, which throws `ArgumentOutOfRangeException`, or text beyond the `int` range, which throws `OverflowException`; those still propagate. In Example B, the inner `catch (IOException)` handles the storage failure and translates it into a domain failure, and the outer `catch (InvalidOperationException)` handles that domain failure while keeping the I/O cause as `InnerException`.',
            why="A catch clause matches by exception type, so each one names exactly the failure category it is prepared to handle. Everything else continues up the call stack unchanged.",
            wrong='Assuming the FormatException catch also covers `ParseCount("-1")` is wrong: `ArgumentOutOfRangeException` is not a `FormatException`, so that call would end the program unless another handler catches it.',
            verify='Call `ParseCount("-1")` inside the same try and confirm the program stops with `ArgumentOutOfRangeException`. In B, check `observed?.InnerException?.Message == "synthetic read failure"`.',
        ),
        2: dict(
            code="""int ParseCount(string text) {
  int value = int.Parse(text, CultureInfo.InvariantCulture);
  if (value < 0)
    throw new ArgumentOutOfRangeException(nameof(text));
  return value;
}
string outcome = "none";
try {
  ParseCount("-2");
} catch (FormatException) {
  outcome = "format";
} catch (ArgumentOutOfRangeException) {
  outcome = "negative";
}
Check(outcome == "negative", "negative is not a format error");""",
            observe="-2 is reported as negative, not as a format error.",
            explain="`-2` is well-formed numeric text, so `int.Parse` succeeds and returns -2. The domain rule then throws `ArgumentOutOfRangeException`, which the second catch clause handles. Keeping the clauses separate lets a caller tell a typing mistake from a valid number that breaks the business rule.",
            wrong="Throwing `FormatException` for the negative value, or catching both cases in one clause, tells the user that `-2` is not a number when the real problem is that counts cannot be negative.",
            verify='Run the same try with `"x"` and confirm `outcome` becomes `format`. Run it with `"3"` and confirm `outcome` stays `none`.',
        ),
        4: dict(
            explain='`string Report(string path) { try { ... } catch (Exception) { return ""; } }` returns an empty string for a missing file, a permission error, malformed data and even a programming bug such as `NullReferenceException`. The caller cannot distinguish any of these from a real report with no rows, so a lost import looks like success. Catch only the failures you can handle and let the others propagate, or return an explicit failure outcome instead of an empty value.',
            why="An empty report is a legitimate successful result for an empty data set. Returning it on failure reuses a valid value as a sentinel, which deletes the evidence the caller needs to retry, alert or stop.",
            wrong="Adding a log line inside the catch-all and still returning the empty report records the failure somewhere nobody is watching, while the caller continues to publish an empty report.",
            verify='Call the catch-all version with a path that does not exist and observe a successful empty result. With the narrowed version, check that the same call throws `FileNotFoundException`, while a real empty file still returns `""`.',
        ),
        5: dict(
            code="""string Classify(string text) {
  try {
    int value = int.Parse(text, CultureInfo.InvariantCulture);
    return "ok " + value;
  } catch (FormatException) {
    return "rejected";
  }
}
Check(Classify("4") == "ok 4", "success");
Check(Classify("four") == "rejected", "expected rejection");
bool escaped = false;
try {
  Classify(null!);
} catch (ArgumentNullException) {
  escaped = true;
}
Check(escaped, "unexpected exception is not swallowed");""",
            observe="4 succeeds, four is rejected as expected and a null argument escapes as ArgumentNullException.",
            explain='Each test targets one path. `"4"` reaches the return value. `"four"` reaches the FormatException clause, which is the expected rejection. Passing `null` makes `int.Parse` throw `ArgumentNullException`, a failure `Classify` was not written to handle, and the third test proves it propagates instead of being turned into `rejected`.',
            wrong="Changing the clause to `catch (Exception)` keeps the first two tests green and turns the null input into `rejected`. Without the third test, nobody would notice that bugs are now being reported as bad user input.",
            verify="Temporarily widen the clause to `catch (Exception)` and confirm the last check fails. Restore `catch (FormatException)` and all three pass.",
        ),
    },
    25: {
        1: dict(
            explain="Example A builds a unique directory name under `Path.GetTempPath()` and creates it, so this run owns that directory and nothing else. Inside the try it writes `note.txt` with UTF-8 without a BOM, checks the file holds five bytes and reads the same text back. The finally block deletes the directory recursively whether the checks passed or threw, and the final check confirms it no longer exists.",
            why="The GUID makes collisions with other runs practically impossible, which is what makes recursive deletion safe: the operation removes only what it created. Placing the cleanup in finally ties it to leaving the try block on any path.",
            wrong="Deleting the directory after the try instead of in finally leaves it behind whenever a check throws. Using a fixed name such as `lesson` lets two concurrent runs delete each other's files.",
            verify="Temporarily make the round-trip check fail and confirm the program stops but `Directory.Exists(root)` is false afterwards. Print `root` once to see that each run gets a different name.",
        ),
        2: dict(
            code="""string id = Guid.NewGuid().ToString("N");
string folder = Path.Combine(Path.GetTempPath(), "lines-" + id);
Directory.CreateDirectory(folder);
try {
  string path = Path.Combine(folder, "lines.txt");
  string text = "first\\nsecond\\n";
  File.WriteAllText(path, text, new UTF8Encoding(false));
  Check(File.ReadAllBytes(path).Length == 13, "13 bytes with two LF");
  string read = File.ReadAllText(path);
  Check(read == text && !read.Contains('\\r'), "LF policy preserved");
  var lines = File.ReadAllLines(path);
  Check(lines.Length == 2 && lines[1] == "second", "two lines");
} finally {
  Directory.Delete(folder, true);
}""",
            observe="The file holds 13 bytes, first, a line feed, second and a final line feed, with no carriage returns.",
            explain="This task builds on Example A, the file round trip. The policy is LF line endings with a final newline, written explicitly as `\\n` instead of `Environment.NewLine`, so the bytes are the same on Linux and Windows. The expected 13 is 5 + 1 + 6 + 1, and reading the text back unchanged shows nothing translated the line endings.",
            wrong='`File.WriteAllLines(path, new[] { "first", "second" })` uses `Environment.NewLine`, which is CRLF on Windows. The same program would then write 15 bytes there, and a byte-level comparison with a Linux run fails.',
            verify='Replace the text with `string.Join(Environment.NewLine, "first", "second") + Environment.NewLine` and compare the byte count on Linux (13) with Windows (15). The explicit `\\n` version gives 13 on both.',
        ),
        4: dict(
            explain='`File.ReadAllText("data/input.csv")` resolves the relative path against `Environment.CurrentDirectory`, the process working directory, not against the source file or the folder of the compiled program. Run from the project folder it finds the file; run from `bin/Debug/net10.0`, a test runner or a container whose working directory is elsewhere, it throws `FileNotFoundException` or reads a different file. Print `Path.GetFullPath("data/input.csv")` to see the real target, then build paths from an explicit base such as a command-line argument or `AppContext.BaseDirectory` with `Path.Combine`.',
            why="The operating system interprets every relative path against the current directory of the process, which the launcher chooses. `Path.GetFullPath` applies the same rule, so it shows exactly which file the program would open.",
            wrong="Copying the data file into every possible working directory makes the symptom disappear on one machine without fixing the assumption. Hardcoding an absolute path from your own computer breaks on every other machine and in the worker.",
            verify='Check `Path.GetFullPath("data/input.csv") == Path.Combine(Environment.CurrentDirectory, "data", "input.csv")`. Then set `Environment.CurrentDirectory` to a temporary directory and confirm the same relative name now points inside it.',
        ),
        5: dict(
            code="""string id = Guid.NewGuid().ToString("N");
string folder = Path.Combine(Path.GetTempPath(), "text-" + id);
Directory.CreateDirectory(folder);
var utf8 = new UTF8Encoding(false);
try {
  string empty = Path.Combine(folder, "empty.txt");
  File.WriteAllText(empty, "", utf8);
  Check(new FileInfo(empty).Length == 0, "empty file has no bytes");
  Check(File.ReadAllText(empty, utf8) == "", "empty round trip");
  string named = Path.Combine(folder, "names.txt");
  string text = "Zoë, Łódź, 東京";
  File.WriteAllText(named, text, utf8);
  Check(text.Length == 13, "13 UTF-16 code units");
  Check(new FileInfo(named).Length == 21, "21 UTF-8 bytes");
  Check(File.ReadAllText(named, utf8) == text, "non-ASCII round trip");
} finally {
  Directory.Delete(folder, true);
}""",
            observe="The empty file has 0 bytes and reads back as empty; the non-ASCII text is 13 code units, 21 bytes and round-trips exactly.",
            explain="An empty write still creates the file, and without a BOM it contains no bytes at all. For the second file the expected sizes were counted independently: `Zoë` is 4 bytes, `Łódź` is 7, `東京` is 6 and the two `, ` separators add 4, giving 21. The round trip proves the same encoding was used for writing and reading.",
            wrong="Writing with `Encoding.UTF8` makes the empty file 3 bytes long, because it starts with a byte order mark even when there is no text. Reading the second file with `Encoding.Latin1` returns mojibake such as `ZoÃ«` instead of `Zoë`.",
            verify="Write the empty file with `Encoding.UTF8` and check its length is 3. Then read the names file with `Encoding.Latin1` and confirm the comparison with `text` fails.",
        ),
    },
    26: {
        1: dict(
            explain="`restored == original` establishes that this record, serialized by `JsonSerializer` and deserialized by the same serializer with the same options, comes back with equal `Name` and `Quantity`. It does not establish that the JSON text matches an agreed external contract, that JSON produced by another system or an older version decodes correctly, that missing or unknown fields are handled the way you intend, or that the decoded value satisfies domain rules such as a nonnegative quantity.",
            why="A round trip tests the serializer against itself. Any naming or default that is wrong in the same way on both sides cancels out, so the test passes even when the wire format would surprise a partner system.",
            wrong="Treating the round trip as a full contract test leads to shipping a renamed property: the round trip still passes, while every stored document and every other client breaks.",
            verify="Add a fixed JSON literal written by hand from the contract, deserialize it, and compare it with an expected record. Example B shows the separate domain check that a round trip cannot provide.",
        ),
        2: dict(
            code=r"""string v1 = "{\"Name\":\"pear\",\"Quantity\":3}";
string v2 = "{\"Version\":2,\"Name\":\"pear\",\"Quantity\":3," +
            "\"Description\":\"green\"}";
string Describe(string json) {
  using var document = JsonDocument.Parse(json);
  var root = document.RootElement;
  int version = 1;
  if (root.TryGetProperty("Version", out var number))
    version = number.GetInt32();
  if (version < 2 || !root.TryGetProperty("Description", out var text))
    return "";
  return text.GetString() ?? "";
}
Check(Describe(v1) == "", "version 1 has no description");
Check(Describe(v2) == "green", "version 2 description");
var old = JsonSerializer.Deserialize<ItemDto>(v2);
Check(old == new ItemDto("pear", 3), "version 1 reader still works");""",
            observe="A version 1 document has no description, a version 2 document yields green and the old ItemDto reader still decodes the version 2 document.",
            explain="The new field is optional and tied to an explicit `Version` number: a document without `Version` is treated as version 1, and only version 2 or later is asked for `Description`. The old `ItemDto` contract keeps working because `System.Text.Json` ignores unknown properties by default, so adding a field is a compatible change for existing readers.",
            wrong="Making `Description` required, or reading it without checking the version, breaks every stored version 1 document. Reusing an existing property name with a new meaning breaks old readers silently instead of loudly.",
            verify="Remove `Description` from `v2` and confirm `Describe` returns an empty string instead of throwing. Change `Version` to 1 in `v2` and confirm the description is ignored.",
        ),
        4: dict(
            explain='`JsonSerializer.Deserialize<ItemDto>("{\\"Name\\":\\"pear\\"}")` succeeds and produces `Quantity` 0. The missing field was filled with the default value of `int`, so the decoder cannot tell "the sender said 0" from "the sender forgot the field". Code that trusts the result records a real zero stock level for data that was never sent. Make the field required: set `RespectRequiredConstructorParameters = true` in `JsonSerializerOptions` for a positional record, mark the property with `[JsonRequired]`, or inspect the document for the property before accepting it.',
            why="By default the serializer binds only what is present and uses `default(T)` for everything else. For a value type, the default is a legal value, so absence leaves no trace in the decoded object.",
            wrong="Checking `item.Quantity == 0` afterwards rejects legitimate zero quantities as well. Making `Quantity` an `int?` without changing the validation only moves the ambiguity, unless null is then rejected explicitly.",
            verify='Decode the document without `Quantity` and observe 0. With the required setting enabled, check that the same call throws `JsonException`, while an explicit `"Quantity":0` still decodes to 0.',
        ),
        5: dict(
            code=r"""bool malformed = false;
try {
  JsonSerializer.Deserialize<ItemDto>("{\"Name\":");
} catch (JsonException) {
  malformed = true;
}
Check(malformed, "malformed JSON throws JsonException");
var nothing = JsonSerializer.Deserialize<ItemDto>("null");
Check(nothing is null, "JSON null decodes to a null reference");
string extra = "{\"Name\":\"pear\",\"Quantity\":2,\"Color\":\"green\"}";
var item = JsonSerializer.Deserialize<ItemDto>(extra);
Check(item == new ItemDto("pear", 2), "unknown field ignored");""",
            observe="Truncated JSON throws JsonException, the literal null decodes to null and an unknown Color field is ignored.",
            explain="The three inputs fail at different layers. Truncated text is not JSON at all, so the parser throws. `null` is valid JSON whose value is nothing, so the result is a null reference even though the declared type is a non-nullable `ItemDto`; the caller must check for it. An extra property is valid JSON that the contract does not mention, and the default policy skips it, which keeps old readers compatible with newer writers.",
            wrong="Using `Deserialize<ItemDto>(json)!` and continuing turns the `null` input into a `NullReferenceException` far from the decoder. Expecting the unknown field to throw assumes a strict policy that is not the default.",
            verify="Pass options with `UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow` for the extra-field case and confirm it now throws `JsonException`. Decide which policy the contract wants and keep a test for it.",
        ),
    },
    28: {
        1: dict(
            explain="In Example A, `-2 -> 0` rejects an identity implementation that returns its input and an absolute-value implementation that returns 2. `0 -> 0` rejects implementations with a wrong default at the boundary, such as `value <= 0 ? 1 : value`. `3 -> 3` rejects implementations that always return 0 or that clamp too much. In Example B, the zero case rejects `Wrong`, and the idempotence check rejects implementations whose second application changes the value, such as one that negates negative numbers.",
            why="A case is useful only if some plausible wrong implementation gives a different answer for it. Each category, negative, boundary and positive, separates a different family of mistakes.",
            wrong="Saying the cases test that the function works overstates them: an implementation that special-cases exactly -2, 0 and 3 would pass. The cases exclude named families of errors, not every error.",
            verify="Write `int Identity(int v) => v;` and `int Zero(int v) => 0;` and confirm each fails at least one case in Example A, and that `Wrong` fails only the zero case.",
        ),
        2: dict(
            code="""Check(ClampNonnegative(int.MinValue) == 0, "most negative clamps to 0");
Check(ClampNonnegative(int.MaxValue) == int.MaxValue, "largest kept");
bool overflow = false;
try {
  Math.Abs(int.MinValue);
} catch (OverflowException) {
  overflow = true;
}
Check(overflow, "an Abs-based clamp would fail at the extreme");""",
            observe="int.MinValue clamps to 0, int.MaxValue is unchanged and Math.Abs(int.MinValue) throws OverflowException.",
            explain="`ClampNonnegative` only compares and returns either 0 or the input, so it never computes a value outside the `int` range. The extreme cases are still worth writing because a plausible alternative implementation, `Math.Abs` or negation, overflows exactly at `int.MinValue`, which has no positive counterpart in two's complement.",
            wrong="Testing only small numbers such as -2 cannot distinguish the correct clamp from a rewrite such as `Math.Abs(value) == value ? value : 0`, which agrees everywhere except at `int.MinValue`, where it throws. Expecting `-int.MinValue` to be positive is the overflow the case is designed to catch.",
            verify="In an `unchecked` context compute `-int.MinValue` and observe that it is still `int.MinValue`. That shows why negation-based clamps return a negative number at the extreme.",
        ),
        4: dict(
            explain="`Check(ClampNonnegative(-2) == ClampNonnegative(-2), ...)` compares the function with itself. Any deterministic implementation, including one that returns -2 or 42, makes both sides equal, so the assertion cannot fail and tests nothing about the contract. Replace the right side with an expected value derived independently from the specification: `Check(ClampNonnegative(-2) == 0, ...)`.",
            why="A test needs an oracle that does not come from the code under test. When both sides are produced by the same call, a bug appears on both sides and cancels out.",
            wrong="Copying the current output into the expected value, such as running the function once and pasting the result, has the same flaw one step removed: the test freezes whatever the code does today, bugs included.",
            verify="Change `ClampNonnegative` temporarily to return its input. The self-comparison still passes, while the independent `== 0` assertion fails. Restore the function afterwards.",
        ),
        5: dict(
            code="""int[] samples = { int.MinValue, -1, 0, 1, int.MaxValue };
foreach (int value in samples) {
  int once = ClampNonnegative(value);
  Check(ClampNonnegative(once) == once, $"idempotent at {value}");
}
Check(ClampNonnegative(-1) == 0, "largest invalid input becomes 0");
Check(ClampNonnegative(0) == 0, "boundary itself is kept");
Check(ClampNonnegative(1) == 1, "smallest positive is kept");""",
            observe="Clamping twice equals clamping once for every sample, and -1, 0 and 1 map to 0, 0 and 1.",
            explain="Idempotence is a property that must hold for any input, so it is checked across extremes and the boundary. The boundary values come from the specification, not from running the code: the rule is that negative inputs become 0, so the boundary sits between -1 and 0, and the cases on each side of it have expected values you can write down before running.",
            wrong="Checking idempotence alone is not enough: a function that always returns 5 is idempotent. The independently derived boundary cases are what tie the property to the actual contract.",
            verify="Replace the body temporarily with `value < -1 ? 0 : value` and confirm the `-1` check fails while idempotence still passes. That shows why both kinds of test are needed.",
        ),
    },
    29: {
        1: dict(
            explain="`pending` is a `Task<int>`: a handle that represents an operation and its eventual outcome, which may be success with a value, failure or cancellation. `value` is the `int` 7 obtained by awaiting that handle. The handle can be stored, passed around, combined with other tasks and inspected with properties such as `IsCompletedSuccessfully`; the integer is just the result and carries no information about how it was produced.",
            why="`await` unwraps the task: it waits for completion, rethrows a stored exception if the task failed and otherwise produces the result. Before the await you hold a promise; after it you hold the value.",
            wrong="Writing `int value = pending;` does not compile, and `pending.Result` blocks the thread and wraps a failure in `AggregateException`. Treating the task as the number confuses the operation with its outcome.",
            verify="Print `pending.GetType()` and `value.GetType()` and compare. Then replace `Task.FromResult(7)` with `Task.FromException<int>(new InvalidOperationException())` and confirm the await throws instead of producing a number.",
        ),
        2: dict(
            code="""var tasks =
    new[] { Task.FromResult(5), Task.FromResult(1), Task.FromResult(3) };
int[] values = await Task.WhenAll(tasks);
Check(values.SequenceEqual(new[] { 5, 1, 3 }), "input order kept");
Check(tasks.All(task => task.IsCompletedSuccessfully), "all completed");""",
            observe="WhenAll returns 5, 1, 3, the order in which the tasks were passed, not a sorted order.",
            explain="The prediction is input order. `Task.WhenAll` places each result at the index of its task in the argument array, regardless of when each task finished. Here the tasks are already complete, so there is no completion order to observe at all, and the output is still not sorted by value.",
            wrong="Expecting 1, 3, 5 confuses the result array with sorting, and expecting the fastest result first confuses it with `Task.WhenAny`. Neither applies to `WhenAll`.",
            verify="Use three `TaskCompletionSource<int>` objects, pass their tasks to `WhenAll`, complete them in reverse order and confirm the awaited array is still in input order.",
        ),
        4: dict(
            explain='`SaveAsync(item); return "saved";` starts the save and returns immediately without awaiting it. If the save fails, the exception is stored in the returned task, which nobody observes, so the caller sees `saved` for data that was never written. Any code after the call also runs before the save has finished. Await the task, `await SaveAsync(item);`, so that failure propagates and ordering is guaranteed.',
            why="An async method reports its failure through its task. Without `await` or another observation of that task, the exception has nowhere to go, and the calling method cannot know the operation failed.",
            wrong="Assigning the task to a discard, `_ = SaveAsync(item);`, only silences the compiler warning; it does not observe the failure. Wrapping the call in `try/catch` without awaiting catches nothing, because the exception is not thrown at the call site.",
            verify='Make the save return `Task.FromException(new IOException("disk"))`. The unawaited version returns `saved`; the awaited version throws `IOException` to the caller.',
        ),
        5: dict(
            code="""int[] ok = await Task.WhenAll(Task.FromResult(1), Task.FromResult(2));
Check(ok.Sum() == 3, "successful parts combined");
var problem = new InvalidOperationException("part failed");
var bad = Task.FromException<int>(problem);
bool failed = false;
try {
  await Task.WhenAll(Task.FromResult(1), bad);
} catch (InvalidOperationException error) {
  failed = error.Message == "part failed";
}
Check(failed, "failure propagated through WhenAll");
int[] none = await Task.WhenAll(Array.Empty<Task<int>>());
Check(none.Length == 0, "empty input completes with no values");""",
            observe="Two successful parts give 3, one failed part makes the await throw its InvalidOperationException and no tasks give an empty array.",
            explain="`WhenAll` succeeds only if every input succeeds. When one input fails, the combined task fails and `await` rethrows the first stored exception, here the one created as `problem`. An empty input is not an error: there is nothing to wait for, so the combined task completes immediately with an empty array, which keeps sums and counts well-defined.",
            wrong="Expecting `AggregateException` from `await` confuses it with `.Wait()` or `.Result`; `await` rethrows the inner exception. Expecting the empty case to hang or throw would make callers special-case an empty batch unnecessarily.",
            verify="Store the combined task in a variable before awaiting it and, inside the catch, check `combined.Exception?.InnerExceptions.Count`. With two failed inputs it is 2, even though `await` threw only the first.",
        ),
    },
    30: {
        1: dict(
            explain="In Example A, the request is `source.Cancel()`, the observation is `ThrowIfCancellationRequested()` throwing `OperationCanceledException`, and the completion is the catch block setting `observed`, after which the check runs. In Example B, the request is again `source.Cancel()`, the observation is `WaitAsync(source.Token)` throwing, and that ends only the wait. The operation itself completes later, when `completion.SetResult(9)` runs, and awaiting `completion.Task` produces 9.",
            why="Cancellation is cooperative: requesting it only sets a flag on the token. Nothing stops until some code observes the token, and the observing code decides what ends. Completion of the underlying work is a separate event that may happen before, after or without the cancellation.",
            wrong="Treating `Cancel()` as the moment the work stops predicts that `completion.Task` can never finish in Example B. It does finish, because nothing that produces it observed the token.",
            verify="Check `completion.Task.IsCompleted` right after the cancelled wait (false) and again after `SetResult` (true). Those two values separate the observation from the completion.",
        ),
        2: dict(
            code="""var state = new List<string>();
using var source = new CancellationTokenSource();
void Apply(string change, CancellationToken token) {
  token.ThrowIfCancellationRequested();
  state.Add(change);
}
Apply("first", source.Token);
source.Cancel();
bool stopped = false;
try {
  Apply("second", source.Token);
} catch (OperationCanceledException) {
  stopped = true;
}
Check(stopped && state.SequenceEqual(new[] { "first" }), "no change");""",
            observe="The first change is applied, the request arrives and the second call stops before adding anything, so the state holds only first.",
            explain="The helper receives the token as a parameter instead of reaching for a global, and it checks the token before the state change. That ordering is the point: if cancellation has been requested, the method exits with no partial effect. A change that was already applied stays applied, because cancellation is not rollback.",
            wrong="Checking the token after `state.Add(change)` lets a cancelled call still mutate the state and then report cancellation, so the caller believes nothing happened when something did.",
            verify="Move the token check below `state.Add` and confirm the state now contains both entries even though the second call reported cancellation.",
        ),
        4: dict(
            explain="A client sends a write, waits with a timeout, and when the wait times out it sends the same write again. The timeout ended only the waiting, as in Example B: the first write may still be running or may already have been committed. Replaying it can apply the change twice, such as two payments or a doubled stock adjustment. Retry only operations that are idempotent, for example by attaching an idempotency key that the server uses to discard repeats, or query the outcome of the first attempt before deciding to send another.",
            why="A timeout is information about the waiter, not about the operation. Without a way to learn the real outcome, the client cannot distinguish a lost request from a slow success.",
            wrong="Making the timeout longer reduces how often the duplicate happens but does not remove it. Cancelling the token after the timeout does not undo work the server already committed.",
            verify="Model the write with a `TaskCompletionSource` and a counter: time out the wait, replay, then complete the first attempt and observe the counter at 2. With an idempotency key checked before incrementing, the same sequence leaves it at 1.",
        ),
        5: dict(
            code="""int runs = 0;
void Work(CancellationToken token) {
  token.ThrowIfCancellationRequested();
  runs++;
}
using var early = new CancellationTokenSource();
early.Cancel();
bool refused = false;
try {
  Work(early.Token);
} catch (OperationCanceledException) {
  refused = true;
}
Check(refused && runs == 0, "cancelled before start: no work");
using var late = new CancellationTokenSource();
Work(late.Token);
late.Cancel();
Check(runs == 1, "cancellation after completion undoes nothing");
var finished = Task.FromResult(4);
Check(await finished.WaitAsync(late.Token) == 4, "completed result kept");""",
            observe="A token cancelled before the call prevents any work; cancelling after the work finished leaves the count at 1 and a completed task still yields 4.",
            explain="Before start, the first observation of the token throws, so the operation does nothing. After completion, nobody observes the token anymore, so the request has no effect on work already done. `WaitAsync` checks whether the task is already complete before looking at the token, so a finished result is returned even with a cancelled token.",
            wrong="Assuming a cancelled token always produces `OperationCanceledException` predicts that the last check throws. Cancellation affects only operations that observe it while they are still running.",
            verify="Replace `finished` with a task from a `TaskCompletionSource` that has not completed and confirm `WaitAsync(late.Token)` now throws `OperationCanceledException`.",
        ),
    },
    31: {
        1: dict(
            explain="Example A, capacity 1: `TryWrite(4)` succeeds and occupancy is 1. `TryWrite(5)` is refused and occupancy stays 1. `ReadAsync()` removes 4 and occupancy is 0. Example B, capacity 2: `TryWrite(2)` makes it 1, `TryWrite(3)` makes it 2 and `Complete()` closes the writer while 2 items remain buffered. The loop reads 2 (occupancy 1) and 3 (occupancy 0), then ends because the channel is both empty and completed. `Completion` finishes and the later `TryWrite(9)` is refused.",
            why="A bounded channel holds at most its capacity. Writes add, reads remove, and completion forbids further writes without discarding what is already buffered.",
            wrong="Assuming `Complete()` clears the buffer predicts a sum of 0 in Example B. Assuming capacity limits only reads predicts that `TryWrite(5)` succeeds in Example A.",
            verify="Print `channel.Reader.Count` after each operation in both examples; the numbers match the trace above.",
        ),
        2: dict(
            code="""var channel = Channel.CreateBounded<int>(3);
var admitted = new List<bool>();
for (int i = 1; i <= 4; i++)
  admitted.Add(channel.Writer.TryWrite(i));
Check(admitted.SequenceEqual(new[] { true, true, true, false }), "cap 3");
Check(channel.Reader.Count == 3, "three items buffered");
Check(await channel.Reader.ReadAsync() == 1, "oldest item first");""",
            observe="With capacity 3, the first three immediate writes succeed, the fourth is refused and the reader receives 1 first.",
            explain="The prediction was three successes and one refusal: with no reader running, every successful `TryWrite` occupies one slot, so the fourth write finds the channel full. The default full mode for `TryWrite` is to refuse rather than wait. Items leave in the order they were admitted.",
            wrong="Expecting the fourth write to wait until space frees up confuses `TryWrite` with `WriteAsync`. Expecting it to replace an older item assumes a `DropOldest` mode that was not configured.",
            verify="After the first read, call `TryWrite(5)` and confirm it succeeds, because reading freed one slot.",
        ),
        4: dict(
            explain='A consumer written as `while (channel.Reader.TryRead(out var item)) Handle(item);` stops the first time the channel is momentarily empty. If the producer is still running, later items are written after the consumer has left and are never handled. An empty open channel means "nothing yet", not "nothing ever". Use `await foreach (var item in channel.Reader.ReadAllAsync())` or a `WaitToReadAsync` loop: both wait while the channel is empty and open, and end only after the writer completes and the buffer drains.',
            why="Only the writer knows when production is finished, and it says so by calling `Complete()`. `TryRead` returning false reports the current occupancy, not that completion signal.",
            wrong="Adding a short delay and checking again makes the race rarer but not impossible, and it ties correctness to timing. Checking `Reader.Count == 0` has exactly the same flaw as `TryRead`.",
            verify="Start a consumer using the `TryRead` loop on an empty channel, then write an item and complete the writer. The item is never handled. With `ReadAllAsync`, the same sequence handles it, and `Reader.Completion` finishes.",
        ),
        5: dict(
            code="""var empty = Channel.CreateBounded<int>(2);
empty.Writer.Complete();
int seen = 0;
await foreach (int value in empty.Reader.ReadAllAsync()) { seen++; }
await empty.Reader.Completion;
Check(seen == 0, "completed empty channel ends at once");
var full = Channel.CreateBounded<int>(2);
full.Writer.TryWrite(7);
full.Writer.TryWrite(8);
Check(!full.Writer.TryWrite(9), "buffer full");
full.Writer.Complete();
int sum = 0;
await foreach (int value in full.Reader.ReadAllAsync()) { sum += value; }
await full.Reader.Completion;
Check(sum == 15, "full buffer drained after completion");""",
            observe="Completing an empty channel ends reading immediately with no items; completing a full channel still delivers 7 and 8.",
            explain="Completion means no more writes, so the reader ends once the buffer is empty. With zero buffered items, that is immediately, and `Completion` finishes without waiting for anything. With a full buffer, the two admitted items are still delivered in order, and only then does reading end. The refused write of 9 was never admitted, so it is not part of the sum.",
            wrong="Expecting `ReadAllAsync` to hang on the empty completed channel confuses completed with open. Expecting the full channel to lose its items on completion would make `Complete()` a discard operation, which it is not.",
            verify="Leave out `empty.Writer.Complete()` and observe that the empty read loop waits forever, which is why completion is the producer's explicit responsibility.",
        ),
    },
    32: {
        1: dict(
            explain="In Example A the syntax stage is `JsonSerializer.Deserialize<ImportItem[]>`: it turns the text into two `ImportItem` values, and it would throw `JsonException` for malformed text or produce null for the literal `null`, which `ImportAsync` turns into `ArgumentException`. The validation stage looks at each item: `pear` with 2 passes, and the item with an empty name fails, so `rejected` becomes 1. The aggregation stage adds only validated quantities with `checked`, giving `Total` 2.",
            why="Each stage answers a different question: is this JSON of the right shape, is each record acceptable, and what do the accepted records add up to. Keeping them separate makes each kind of failure visible in its own way.",
            wrong="Merging validation into aggregation, for example summing everything and subtracting invalid quantities afterwards, makes a negative quantity look like a correction instead of a rejection.",
            verify="Feed `[{]` (syntax failure), an item with a negative quantity (validation failure) and two valid items (aggregation) and confirm the three different outcomes.",
        ),
        2: dict(
            code=r"""string pear2 = "{\"Name\":\"pear\",\"Quantity\":2}";
string pear3 = "{\"Name\":\"pear\",\"Quantity\":3}";
string json = $"[{pear2},{pear3}]";
var result = await ImportAsync(json, CancellationToken.None);
Check(result.Total == 5 && result.Rejected == 0, "quantities summed");
var items = JsonSerializer.Deserialize<ImportItem[]>(json)!;
var names = items.Select(item => item.Name);
int distinct = names.Distinct(StringComparer.Ordinal).Count();
Check(distinct == 1, "distinct item count is a separate measure");""",
            observe="Two valid pear records give Total 5 with no rejections, while the number of distinct names is 1.",
            explain="The documented decision is that `Total` reports total quantity: a repeated valid name is a second delivery of the same item, so its quantity is added, not rejected and not deduplicated. The distinct item count is a different measure, 1 here, and is computed separately when a report needs it. Writing both down prevents a reader from interpreting `Total` 5 as five distinct items.",
            wrong="Deduplicating by name before summing would report 2 or 3 depending on which record wins, silently discarding a real delivery. Reporting `Total` as the number of records would conflate quantity with rows.",
            verify="Add a third record named `Pear` with quantity 1 and confirm `Total` becomes 6 while the ordinal distinct count becomes 2, which shows the case policy also has to be stated.",
        ),
        4: dict(
            explain="`try { return await ImportAsync(json, token); } catch (Exception) { return new ImportResult(0, 0); }` catches `OperationCanceledException` along with every other failure and returns the same value as a successful import of an empty array. Example B shows that these must differ: a cancelled request did not produce a report at all. Let cancellation propagate, for example with `catch (Exception error) when (error is not OperationCanceledException)`, and represent invalid input with its own outcome instead of an empty report.",
            why="The caller decides what to do from the outcome. A user who cancelled should see a cancellation, a broken file should be reported as invalid, and only a valid empty array should produce `Total` 0 with no rejections.",
            wrong="Logging the exception inside the catch-all and still returning the empty report does not fix it: the caller still publishes a report claiming the import succeeded with nothing in it.",
            verify="Call the catch-all wrapper with a cancelled token and with `[]` and observe identical results. With the narrowed catch, check that the cancelled call throws `OperationCanceledException` and the `[]` call returns `Total` 0.",
        ),
        5: dict(
            code=r"""async Task<string> Outcome(string json) {
  try {
    var result = await ImportAsync(json, CancellationToken.None);
    return $"total {result.Total} rejected {result.Rejected}";
  } catch (JsonException) {
    return "malformed";
  } catch (ArgumentException) {
    return "not an array";
  }
}
string negative = "[{\"Name\":\"pear\",\"Quantity\":-1}]";
string fraction = "[{\"Name\":\"pear\",\"Quantity\":2.5}]";
Check(await Outcome("[{") == "malformed", "malformed JSON");
Check(await Outcome("null") == "not an array", "JSON null");
Check(await Outcome("[]") == "total 0 rejected 0", "empty list");
Check(await Outcome(negative) == "total 0 rejected 1", "negative");
Check(await Outcome(fraction) == "malformed", "non-integer quantity");""",
            observe="Malformed text and a fractional quantity are malformed, null is not an array, the empty list is a successful empty report and a negative quantity is one rejection.",
            explain="Each input reaches a different stage. `[{` and `2.5` fail during decoding, because a fraction cannot be read as an `int`. `null` decodes to a null array, which the service rejects with `ArgumentException`. `[]` passes every stage and produces a real empty report. `-1` decodes but fails validation, so it is counted as rejected instead of stopping the whole import.",
            wrong="Treating `2.5` as a validation rejection, or `null` as an empty list, would merge different failures into one outcome. Those are exactly the distinctions the service is designed to keep.",
            verify="Add an item with quantity `2147483647` next to one with quantity 1 and confirm the `checked` addition throws `OverflowException`, a fourth outcome the wrapper does not catch.",
        ),
    },
    33: {
        1: dict(
            explain="`value++` inside `LockedCounter.Add` is three logical steps: read the current `value` into a register, add 1 to that copy, and write the copy back to the field. Without the lock, two tasks can both read 41, both compute 42 and both write 42, so one increment disappears even though neither task failed. The `lock (gate)` statement makes the read, add and write one indivisible step with respect to every other code path that takes the same gate, which is why Example A always ends at 400.",
            why="The lost update is not visible in any single line of code; it only appears when you split the line into the steps the processor actually performs. Naming the steps shows exactly which window the lock closes.",
            wrong="Assuming `++` is atomic because it is one operator, or protecting only the write, leaves the read and the write separable and still loses updates under contention.",
            verify="Temporarily replace `lock (gate) value++;` with `value++;`, run Example A several times with more iterations, and observe totals below the expected count.",
        ),
        2: dict(
            code="""var counter = new LockedCounter();
const int tasks = 8;
const int perTask = 250;
void AddMany() {
  for (int i = 0; i < perTask; i++)
    counter.Add();
}
var work = new List<Task>();
for (int t = 0; t < tasks; t++)
  work.Add(Task.Run(AddMany));
await Task.WhenAll(work);
Check(counter.Value == tasks * perTask, "exact total 2000");""",
            observe="Eight tasks of 250 increments each end at exactly 2000.",
            explain="The expected total is the product of task count and increments per task, so it is computed from the same constants the loop uses instead of being typed separately. Doubling the tasks and changing the per-task count does not change the reasoning: every `Add` passes through the same gate, so no increment is lost no matter how the tasks interleave, and `Task.WhenAll` guarantees all of them finished before `Value` is read.",
            wrong="Reading `Value` before awaiting `Task.WhenAll`, or hardcoding 800 after changing the constants, produces a check that fails or passes for the wrong reason.",
            verify="Change `tasks` to 16 and `perTask` to 1000 and confirm the check still passes with 16000 without editing the expected value.",
        ),
        4: dict(
            explain="Two locks form a cycle when task 1 takes `accountA` and then waits for `accountB`, while task 2 takes `accountB` and then waits for `accountA`. Each holds the lock the other needs, so both wait forever and nothing throws. The repair is a global acquisition order: every code path that needs both locks takes them in the same order, for example the account with the smaller identifier first, regardless of the direction of the transfer. With one order, a task can only ever wait for a lock ranked above one it holds, so no cycle can form.",
            why="Deadlock needs a cycle in the wait-for graph. An ordering rule removes cycles by construction, which is stronger than hoping the timing never lines up.",
            wrong="Adding a timeout or a retry hides the symptom and can livelock; taking the locks in the order of the transfer arguments keeps the cycle, because transfer(A, B) and transfer(B, A) still disagree.",
            verify="Write a transfer that orders the two locks by identifier, run many A to B and B to A transfers concurrently, and confirm they all finish and the sum of balances is unchanged.",
        ),
        5: dict(
            code="""var idle = new LockedCounter();
Check(idle.Value == 0, "zero operations read 0");
var live = new LockedCounter();
void Write() {
  for (int i = 0; i < 1000; i++)
    live.Add();
}
int Sample() => live.Value;
var writer = Task.Run(Write);
var samples = new List<Task<int>>();
for (int r = 0; r < 4; r++)
  samples.Add(Task.Run(Sample));
int[] during = await Task.WhenAll(samples);
await writer;
Check(during.All(v => v >= 0 && v <= 1000), "each read is a whole count");
Check(live.Value == 1000, "final total exact");""",
            observe="A fresh counter reads 0, every concurrent read lies between 0 and 1000, and the final value is exactly 1000.",
            explain="With zero operations nothing has written the field, so the reader sees the default 0 and taking the lock is harmless. During writes, each reader takes the same gate as `Add`, so it observes the counter between two whole increments, never in the middle of one. The exact value a reader sees depends on timing, which is why the check states a range instead of a number; only the final value after `await writer` is exact.",
            wrong="Asserting that the concurrent readers see a specific value such as 500 makes the test depend on scheduling and fail at random.",
            verify="Add a fifth reader after `await writer` and confirm it always sees 1000, while the readers started during the writes may differ between runs.",
        ),
    },
    40: {
        1: dict(
            explain="In `StampService` the policy is the rule that an identity must be present and that a stamp is the instant in round-trip `O` format, a colon and the identity. The mechanism is where the instant comes from: `IClock` is the port, and `FixedClock` here or a system clock in production is the adapter. Example A changes only the mechanism and the format rule still applies; Example B shows a different clock cannot bypass the identity rule.",
            why="Policy is what the business would argue about; mechanism is how the program reaches the outside world. Keeping them apart lets you test the policy without real time and change the clock without touching the rule.",
            wrong="Calling the `FixedClock` record part of the domain policy confuses a test adapter with the rule it serves.",
            verify="List which lines would change if the stamp format changed (policy) and which would change if time came from a network service (mechanism); no line should be on both lists.",
        ),
        2: dict(
            code="""var utc = TimeSpan.Zero;
var instant = new DateTimeOffset(2025, 6, 15, 9, 30, 0, utc);
var service = new StampService(new FixedClock(instant));
string stamp = service.Stamp("order-7");
string expected = "2025-06-15T09:30:00.0000000+00:00:order-7";
Check(stamp == expected, "predicted stamp");
var epoch = new StampService(new FixedClock(DateTimeOffset.UnixEpoch));
Check(epoch.Stamp("order-7") != stamp, "only the clock changed");""",
            observe="The second clock produces 2025-06-15T09:30:00.0000000+00:00:order-7, written down before running.",
            explain="Because the clock is injected, the timestamp is fully determined by the supplied instant, and the round-trip `O` format always shows seven fractional digits and the offset. That makes the full string predictable, so the check compares it exactly. The same identity with the Unix epoch clock produces a different stamp, which shows the clock is the only input that changed.",
            wrong='Predicting `2025-06-15T09:30:00Z` forgets that `DateTimeOffset` formats its offset as `+00:00`, and comparing only `StartsWith("2025")` would not catch a wrong format.',
            verify="Change the instant to 2025-06-15 09:30 at offset +02:00 and predict the new string before running.",
        ),
        4: dict(
            explain='A method such as `public string Stamp(string id) => DateTimeOffset.UtcNow.ToString("O") + ":" + id;` inside a class that received `IClock clock` ignores its dependency. Every test that supplies a `FixedClock` still passes for the identity rule, but the timestamp is now the real time, so any test that checks the stamp becomes flaky or has to be loosened. Fix it by reading `clock.Now` everywhere in the domain and leaving `DateTimeOffset.UtcNow` only in the production `IClock` adapter.',
            why="Accepting a dependency documents a promise that the method's results depend only on what was injected. Reaching around it breaks that promise silently.",
            wrong="Making the test tolerant, for example checking only that the stamp is not empty, hides the bug instead of fixing it.",
            verify="Search the domain code for `UtcNow` and `Now` outside the clock adapter, then run Example A's exact-prefix check with an instant in a past year; it fails while the bug is present.",
        ),
        5: dict(
            code="""var utc = TimeSpan.Zero;
var edge = new DateTimeOffset(2024, 12, 31, 23, 59, 59, utc);
var service = new StampService(new FixedClock(edge));
string yearEnd = "2024-12-31T23:59:59.0000000+00:00:a";
Check(service.Stamp("a") == yearEnd, "year end");
var next = new StampService(new FixedClock(edge.AddSeconds(1)));
string newYear = "2025-01-01T00:00:00.0000000+00:00:a";
Check(next.Stamp("a") == newYear, "next second is next year");
var plusTwo = edge.ToOffset(TimeSpan.FromHours(2));
var local = new StampService(new FixedClock(plusTwo));
string shifted = "2025-01-01T01:59:59.0000000+02:00:a";
Check(local.Stamp("a") == shifted, "same instant, next date");
bool Rejects(string id) {
  try {
    service.Stamp(id);
    return false;
  } catch (ArgumentException) {
    return true;
  }
}
Check(Rejects("") && Rejects("   "), "blank identity rejected");""",
            observe="The last second of 2024 stamps as 2024-12-31, one second later is 2025-01-01, the same instant at +02:00 already reads 2025-01-01, and empty or blank identities are rejected.",
            explain="A fixed clock lets the test stand exactly on the boundary. One added second crosses the year, and the same instant viewed at offset +02:00 is already on the next calendar date, so a stamp's date depends on the offset as well as the instant. The identity rule runs before the clock is read, so it rejects both the empty string and whitespace regardless of the instant.",
            wrong="Assuming the date part identifies the day independent of offset leads to reports that put the same event on two different days.",
            verify="Compare `edge == plusTwo` and confirm it is true even though the stamps differ, which shows they are the same instant.",
        ),
    },
    42: {
        1: dict(
            explain="In a request trace, identity answers who is calling: an authenticated subject such as `user-17` established by a verified token. Permission answers what that subject may do: whether the action `report:read` is in the set granted to it. Example A only has the permission step, a `HashSet<string>` with `StringComparer.Ordinal` containing `report:read`. A trace should show both separately: subject authenticated, then action checked against the grants, then allowed or denied.",
            why="Knowing who someone is never implies what they may do. Keeping the steps apart makes a denied request explainable as either an unknown caller or a known caller without that right.",
            wrong="Treating a successful login as permission to everything, or checking permission against a name the caller typed, merges the two steps and removes the boundary.",
            verify="Trace one request where the identity is valid but `report:delete` is denied, and one where the token is missing so the permission check never runs.",
        ),
        2: dict(
            code="""var rights = new HashSet<string>(StringComparer.Ordinal);
rights.Add("report:read");
rights.Add("audit:read");
Check(rights.Contains("audit:read"), "second read allowed");
Check(!rights.Contains("audit:write"), "audit write still denied");
Check(!rights.Contains("report:write"), "no write implied");
bool IsRead(string right) {
  return right.EndsWith(":read", StringComparison.Ordinal);
}
Check(rights.All(IsRead), "every grant is a read");""",
            observe="`audit:read` is allowed, neither `audit:write` nor `report:write` is, and every grant ends in `:read`.",
            explain="The allowlist grants exact action names, so adding `audit:read` grants that one action and nothing related to it. Write access is denied because it is absent, not because a rule removed it. The last check states the intended property of this role directly: it holds only read actions, so a later edit that adds a write grant fails visibly.",
            wrong='Granting `audit:*` or checking `right.StartsWith("audit")` would admit `audit:write` and `audit:delete` along with the read.',
            verify="Add `audit:write` to the set and observe that both the write check and the read-only check fail.",
        ),
        4: dict(
            explain='If the handler reads `{"user":"u1","isAdmin":true}` and uses `isAdmin` to grant access, the caller has chosen its own permissions: anyone can type `true`. The request body is untrusted data, like any other input. The server must derive roles from the authenticated identity, for example by looking up grants for the subject from a verified token, and ignore or reject a privilege field in the body.',
            why="A security boundary only works if the side that decides cannot be influenced by the side being checked. A flag supplied by the client is on the wrong side of the boundary.",
            wrong="Validating that `isAdmin` is a boolean, or hiding the field in the user interface, does not help: a crafted request can still send `true`.",
            verify="Send the same request with `isAdmin` set to true from a non-admin identity and confirm the server still denies admin actions and its decision trace mentions the stored grants, not the body.",
        ),
        5: dict(
            code="""var rights = new HashSet<string>(StringComparer.Ordinal);
rights.Add("report:read");
Check(rights.Contains("report:read"), "exact action allowed");
Check(!rights.Contains("report:delete"), "missing permission denied");
Check(!rights.Contains(""), "empty action denied");
Check(!rights.Contains("Report:read"), "case variant denied");
Check(!rights.Contains("REPORT:READ"), "upper case denied");
Check(!rights.Contains("report:read "), "trailing space denied");""",
            observe="Only the exact string `report:read` is allowed; a missing permission, an empty action, case variants and a trailing space are all denied.",
            explain="The documented policy is ordinal: action names are identifiers compared byte for byte, so `Report:read` is a different, ungranted action. Denying near matches fails closed. If the product decided action names were case-insensitive, that would be a separate, written decision implemented by constructing the set with `StringComparer.OrdinalIgnoreCase`, never by lowercasing some inputs and not others.",
            wrong="Calling `ToLower()` on the request before the check while the set uses `Ordinal` creates a policy nobody wrote down, and it differs from culture-sensitive lowercasing in some locales.",
            verify="Build a second set with `StringComparer.OrdinalIgnoreCase` and confirm the case variants are allowed there but the trailing space and the empty action are still denied.",
        ),
    },
    43: {
        1: dict(
            explain="`dotnet restore` resolves the projects' package and framework references into `obj/project.assets.json` from the configured feeds. `dotnet build` compiles against those resolved assets into `bin`, and fails with NETSDK1004 if the assets file is missing. `dotnet run` builds if needed and then starts the program; with `--no-build` it only runs the existing output. `dotnet publish` produces a deployable folder for a chosen configuration and, optionally, a runtime identifier. In the worker image the DomainLab sequence was: restore exit 0, build exit 0 with 0 warnings and 0 errors, run printed `DomainLab: seven contract checks passed`.",
            why="Each command can fail for a different reason: restore for feeds and versions, build for code, run for behavior, publish for deployment shape. Knowing which step failed tells you where to look.",
            wrong="Reading a successful restore as a successful build, or a successful build as passing checks, skips the evidence each later step provides.",
            verify="Delete `obj`, run `dotnet build --no-restore` and see NETSDK1004, then restore and build again.",
        ),
        2: dict(
            explain="DomainLab is two projects: `Domain` is a class library and `Checks` is an executable that references it, with a local `NuGet.Config`. Built offline in the csharp worker image (SDK 10.0.404, `--network none`) with no package added: `dotnet restore Checks/Checks.csproj --configfile NuGet.Config` exit 0; `dotnet build Checks/Checks.csproj --no-restore` exit 0 with 0 warnings and 0 errors, which also built `Domain` through the project reference; `dotnet run --project Checks/Checks.csproj --no-build` printed `DomainLab: seven contract checks passed` with exit 0.",
            why="Building through the executable proves both projects compile and the reference is correct, and running the checks proves the behavior, not just the compilation.",
            wrong="Adding a package to make something build, or running `dotnet build` on only `Domain`, changes or skips the thing the task asks you to verify.",
            verify="Run the three commands yourself and confirm the same exit codes and the exact `seven contract checks passed` line.",
        ),
        3: dict(
            explain="A pure domain type has no input or output of its own, so it belongs in `Domain`. The reference moved this rule into `Domain/RestockRule.cs`:\n\n```csharp\nnamespace Journey.Domain;\n\npublic sealed record RestockRule(string Name, int Minimum) {\n  public bool Needs(Report report) {\n    ArgumentNullException.ThrowIfNull(report);\n    report.Totals.TryGetValue(Name, out int total);\n    return total < Minimum;\n  }\n}\n```\n\nand added three checks to `Checks/Program.cs`: pear with total 6 does not need restocking at minimum 5, apple with total 3 does, and a missing item counts as 0. In the worker image, `grep Console Domain/*.cs` found nothing, the rebuild succeeded with 0 warnings, and the run printed `DomainLab: ten contract checks passed`.",
            why="The library stays reusable and testable only if it depends on nothing above it. The executable may depend on the library, never the reverse.",
            wrong="Putting `Console.WriteLine` inside the rule, or referencing `Checks` from `Domain`, makes the core depend on one particular program and creates a circular reference.",
            verify="Search `Domain` for `Console`, `File` and `Environment` and confirm none appear, then run the checks and see the new count.",
        ),
        4: dict(
            explain="DomainLab targets `net10.0`, and Example B confirms the compiled framework is `.NETCoreApp,Version=v10.0`. An API added in a later framework, such as `System.Threading.Lock` from .NET 9, does not exist in the `net8.0` reference assemblies, so retargeting a project that uses it fails to compile with CS0246 (type not found) or CS0117 (member not found), not at run time. In the offline worker image the retarget fails even earlier: `dotnet restore` reports NU1100 `Unable to resolve 'Microsoft.NETCore.App.Ref (= 8.0.34)' for 'net8.0'`, because the net8.0 targeting pack is not in the local feed. Diagnose by reading the error code first: NU means restore, CS means compile.",
            why="The target framework decides which API surface the compiler sees. The SDK version only decides which tools are running.",
            wrong="Upgrading the SDK, or assuming that because the program runs on a .NET 10 runtime it can use any .NET 10 API while targeting `net8.0`, confuses the SDK and runtime with the target.",
            verify="Check the `<TargetFramework>` in each `.csproj`, then guard a newer API with `#if NET9_0_OR_GREATER` or keep the target at `net10.0`.",
        ),
        5: dict(
            explain="The lab-owned outputs are exactly `Checks/bin`, `Checks/obj`, `Domain/bin` and `Domain/obj`. In the worker image, after deleting those four with `rm -rf`, no `bin` or `obj` directory remained and the SHA-256 list of every `.cs`, `.csproj` and `NuGet.Config` file was identical before and after (`cmp` exit 0). `dotnet build --no-restore` then failed with NETSDK1004 because `obj/project.assets.json` was gone, which is expected; after `dotnet restore --configfile NuGet.Config` the build succeeded with 0 warnings and the run printed the same passing line as before.",
            why="A clean rebuild proves the result comes from the sources and configuration in the repository, not from stale outputs left by an earlier build.",
            wrong="Running `git clean -fdx` or deleting a home-directory NuGet cache removes files the task does not own and can destroy unrelated work.",
            verify="Record source hashes, delete only the four output folders, restore, build and run, and confirm the hashes match and the checks pass.",
        ),
    },
    44: {
        1: dict(
            explain="The `Event` record carries four fields: `OperationId` correlates events from one run, `Stage` says where in the pipeline it happened, `Outcome` is a fixed vocabulary such as accepted or rejected, and `Count` is how many records share that outcome. All four are safe because none contains raw input. The event population is one event per operation, stage and outcome, so in Example B the accepted and rejected events for `op-7` together describe all five submitted records.",
            why="Knowing the population lets a reader sum events correctly; knowing the fields are safe lets the events be retained and shared without exposing data.",
            wrong="Treating each event as one record would make `Count` 3 look like a single item, and adding the rejected line text would put user content into telemetry.",
            verify="Sum `Count` over the events of one operation and confirm it equals the submitted count, and list each field with a reason it is safe.",
        ),
        2: dict(
            code="""string raw = "pear,-1,secret-note";
var evt = new Event("fixture-1", "parse", "rejected", 1);
string json = JsonSerializer.Serialize(evt);
using var parsed = JsonDocument.Parse(json);
var root = parsed.RootElement;
Check(root.GetProperty("Stage").GetString() == "parse", "stage recorded");
Check(!json.Contains(raw, StringComparison.Ordinal), "raw line absent");
bool leaked = json.Contains("secret", StringComparison.Ordinal);
Check(!leaked, "input content absent");
Check(root.EnumerateObject().Count() == 4, "no extra fields");""",
            observe="The event records stage `parse` with outcome `rejected`, and neither the raw line nor any part of its content appears in the JSON.",
            explain="The new stage value is a fixed label that says where the rejection happened, which is useful operational evidence on its own. The raw line is deliberately not passed to the event, so the serialized JSON contains only the four declared fields. The last check guards that shape, so adding a `Line` field later fails visibly instead of quietly leaking input.",
            wrong="Including the rejected line `for debugging` turns telemetry into a copy of user data, with all the retention and access obligations that come with it.",
            verify="Serialize an event with a fifth, raw-content field in an anonymous object and confirm the content check fails.",
        ),
        4: dict(
            explain="If the handler runs `accepted++` and then `await store.SaveAsync(items)`, a failed or cancelled save still leaves the success metric incremented. The dashboard then reports records as accepted that were never persisted, and the accepted plus rejected events no longer reconcile with what is in storage. Increment the metric after the save completes, or record the outcome from the result of the save, and emit a failed outcome if it throws.",
            why="An outcome metric must describe what happened, not what was attempted. Recording it after the effect it claims is what makes it evidence.",
            wrong="Decrementing the counter in a catch block is fragile: a cancellation or a crash between the two steps still leaves the wrong value.",
            verify="Make the save throw for one batch and confirm the accepted count does not change while a failure event for that operation appears.",
        ),
        5: dict(
            code="""string Rate(int rejected, int submitted) {
  if (submitted == 0)
    return "no data";
  double rate = (double)rejected / submitted;
  return rate.ToString("0.##", CultureInfo.InvariantCulture);
}
Check(Rate(0, 0) == "no data", "no data, not 0 and not NaN");
Check(Rate(0, 5) == "0", "zero rejections is a real 0");
Check(Rate(2, 5) == "0.4", "rate with data");
Check(double.IsNaN(0.0 / 0), "naive division gives NaN");
Event[] none = Array.Empty<Event>();
Check(none.Sum(e => e.Count) == 0, "no events account for 0 records");""",
            observe="With zero submitted records the rate reads `no data`, while zero rejections out of five is a real 0 and two out of five is 0.4.",
            explain="With no submitted records, a rejection rate is undefined. `0.0 / 0` gives NaN, which serializes poorly and poisons averages, and reporting 0 would claim a perfect run that never happened. Checking `submitted == 0` before dividing keeps no data separate from a measured zero, so the report shows `no data` for the first case and `0` for the second. A `double?` that is null for no data is an equivalent choice when the value feeds code instead of a report.",
            wrong="Returning 0 for an empty run hides outages: a pipeline that received nothing looks identical to one that rejected nothing.",
            verify="Serialize `0.0 / 0` with `JsonSerializer` and observe that the default serializer refuses to write NaN, which is another reason to represent no data explicitly.",
        ),
    },
    46: {
        1: dict(
            explain="A collection expression has no type of its own; the declared target chooses it. In Example A, `int[] values = [1, 2, 3];` creates an `int[]` of length 3, and `List<int> list = [..values, 4];` creates a `List<int>` by copying the three values and appending 4. The same brackets would build a `Span<int>`, an `ImmutableArray<int>` or, for an interface target such as `IEnumerable<int>`, a compiler-chosen type that implements it. Writing `var x = [1, 2];` does not compile because there is no target to choose from.",
            why="Knowing the target type tells you what the expression costs and what you can do with the result: an array has a fixed length, a list can grow.",
            wrong="Assuming `[...]` always builds a list, or that it is lazy like a LINQ query, leads to wrong expectations about mutation and evaluation time. Both collections in Example A are built immediately.",
            verify="Print `values.GetType()` and `list.GetType()` and confirm `System.Int32[]` and `System.Collections.Generic.List`1[System.Int32]`.",
        ),
        2: dict(
            code="""List<int> none = [];
int[] empty = [];
Check(none.Count == 0 && empty.Length == 0, "both empty");
Check(empty.GetType() == typeof(int[]), "target decides the type");
none.Add(1);
Check(none.Count == 1, "the empty list is a new mutable list");
IEnumerable<int> view = [];
Check(!view.Any(), "interface target is also empty");""",
            observe="`[]` produces an empty `List<int>`, an empty `int[]` and an empty sequence, chosen by each declaration; the list can then grow.",
            explain="An empty collection expression is only valid with an explicit target, because nothing inside the brackets could suggest a type. Each declaration supplies one: a new empty list that can be added to, a zero-length array and, for the interface, an empty sequence. This replaces `new List<int>()` and `Array.Empty<int>()` without changing what the program does.",
            wrong="Writing `var none = [];` fails with a compile error, and assuming the array version can grow like the list confuses the two targets.",
            verify="Try `var none = [];` and read the compiler error, then restore the explicit type.",
        ),
        3: dict(
            explain="Before, with validation in an ordinary constructor:\n\n```csharp\npublic sealed class ScaleBefore {\n  private readonly int factor;\n  public ScaleBefore(int factor) {\n    ArgumentOutOfRangeException.ThrowIfNegative(factor);\n    this.factor = factor;\n  }\n  public int Apply(int value) => checked(value * factor);\n}\n```\n\nAfter, with a primary constructor:\n\n```csharp\npublic sealed class Scale(int factor) {\n  private readonly int factor =\n      factor >= 0 ? factor : throw new ArgumentOutOfRangeException(nameof(factor));\n  public int Apply(int value) => checked(value * factor);\n}\n```\n\nThe validation moves into the field initializer, which runs during construction, so a negative factor is still rejected before the object exists. The `readonly` field keeps the value immutable, which a bare primary constructor parameter would not. Both classes were compiled together in the csharp worker image and gave the same results for -2, 0 and 4, both threw `OverflowException` for `int.MaxValue`, and both rejected -1.",
            why="A refactor is only safe if it keeps every observable behavior: results, exceptions and immutability. A side-by-side check proves that instead of assuming it.",
            wrong="Writing `public sealed class Scale(int factor) { public int Apply(int value) => checked(value * factor); }` drops the validation and leaves `factor` as a mutable captured parameter, so `new Scale(-1)` would now succeed.",
            verify="Construct both versions with -1, 0 and 3 and compare `Apply` for several inputs, including `int.MaxValue`.",
        ),
        4: dict(
            explain="The language version, not the runtime, decides which syntax compiles. Compiling Example B's syntax in the worker image with `-p:LangVersion=13` failed with CS9260 `Feature 'null conditional assignment' is not available in C# 13.0` and CS9260 `Feature 'unbound generic types in nameof operator' is not available in C# 13.0`, and with `LangVersion=12` the `\\e` escape failed with CS9202. The same code compiled under the default for `net10.0`, which is C# 14. Diagnose by reading the feature name and version in the error, then either target a framework whose default language supports it or rewrite the code in the older syntax.",
            why="Each target framework has a default language version. Copied code carries assumptions about that version that are invisible until the compiler names them.",
            wrong="Setting `<LangVersion>latest</LangVersion>` or `preview` as an unexplained fix can produce code that compiles against a runtime that does not support it, and it hides the real mismatch.",
            verify="Replace `missing?.Capacity = 32;` with `if (missing is not null) missing.Capacity = 32;` and confirm it compiles at C# 13.",
        ),
        5: dict(
            code="""int[] nothing = [];
List<int> spread = [..nothing];
Check(spread.Count == 0, "empty spread adds nothing");
List<int> mixed = [0, ..nothing, 9];
Check(mixed.SequenceEqual(new[] { 0, 9 }), "neighbors kept");
var zero = new Scale(0);
Check(zero.Apply(5) == 0, "zero scaling");
Check(zero.Apply(int.MaxValue) == 0, "zero cannot overflow");""",
            observe="Spreading an empty array adds no elements, the surrounding elements stay in order, and a zero factor maps every input, even `int.MaxValue`, to 0.",
            explain="A spread copies each element of its source, so an empty source contributes nothing and does not insert a placeholder. Scaling by 0 is a valid edge, not an error: `checked(value * 0)` is always 0, so even the largest input cannot overflow.",
            wrong="Expecting `[..nothing]` to throw, or to contain a default 0, confuses an empty spread with a missing value; expecting zero scaling to be rejected adds a rule `Scale` does not have.",
            verify="Spread `nothing` twice into the same list and confirm the count is still the number of literal elements.",
        ),
    },
    47: {
        1: dict(
            explain='In Example A the first `Apply("op-1", 3)` finds no record, adds 3 to `Total` and stores `(3, 3)` under `op-1`; the effect is the change to `Total` and the receipt is the returned 3. The repeated call finds `op-1`, sees the same amount, and returns the stored result 3 without touching `Total`. So there is one effect and two identical receipts, and `Total` stays 3.',
            why="Separating the effect from the receipt is what makes a retry safe: the caller can ask again and get the original answer without causing the effect twice.",
            wrong="Recomputing the receipt from the current `Total` instead of storing it would make an old operation's reply change after later operations run.",
            verify="Apply `op-2` with 3 between the two `op-1` calls and confirm the replayed `op-1` receipt is still 3 while `Total` is 6.",
        ),
        2: dict(
            code="""var ledger = new Ledger();
ledger.Apply("op-1", 3);
ledger.Apply("op-2", 3);
int third = ledger.Apply("op-3", 5);
Check(third == 11 && ledger.Total == 11, "predicted total 11");
Check(ledger.Apply("op-3", 5) == 11 && ledger.Total == 11, "op-3 replay");""",
            observe="The third unique operation brings the total to 11, as predicted, and repeating it returns 11 again without changing the total.",
            explain="Each new identity applies once, so the prediction is 3 plus 3 plus 5, which is 11. The receipt for `op-3` is the total right after its effect, 11, and a retry of `op-3` replays that stored receipt instead of adding 5 again.",
            wrong="Predicting 16 after the retry counts the replay as a second effect.",
            verify="Apply `op-4` with 0 and predict whether the total changes and what its receipt is before running.",
        ),
        4: dict(
            explain='The client sends `Apply("op-1", 3)`, the server applies it, and the reply is lost, so the client sees a timeout. The outcome is unknown, not failed. If the client retries with a fresh identity, `op-1b`, the ledger has no record of it and applies 3 again, so `Total` becomes 6 for one intended payment. The retry must reuse the original identity so the server can recognize it and replay the receipt; generate the identity once per intended operation, before the first attempt, and persist it with the request.',
            why="Idempotency depends on the server seeing the same key for the same intent. A new key tells the server it is a new operation.",
            wrong="Not retrying at all loses operations whose request never arrived, and retrying with a new key duplicates operations whose request did arrive. Only a stable key covers both cases.",
            verify="Simulate the lost reply by ignoring the first return value, retry once with the same identity and once with a fresh one, and compare totals of 3 and 6.",
        ),
        5: dict(
            code="""var ledger = new Ledger();
int first = ledger.Apply("op-9", 4);
int same = ledger.Apply("op-9", 4);
Check(first == 4 && same == 4 && ledger.Total == 4, "identical replays");
bool conflict = false;
try {
  ledger.Apply("op-9", 5);
} catch (InvalidOperationException) {
  conflict = true;
}
Check(conflict && ledger.Total == 4, "conflict rejected, no effect");
Check(ledger.Apply("op-9", 4) == 4, "original receipt still valid");""",
            observe="The identical repeat replays receipt 4; the conflicting payload throws `InvalidOperationException`, leaves the total at 4, and the original request still replays.",
            explain="The ledger stores the payload with the receipt, so it can tell a retry from a different command reusing a key. An identical payload is a retry and gets the stored answer. A different amount under the same key is a client error: applying it would change the meaning of a recorded operation and replaying the old receipt would hide the mistake, so it is rejected before any effect. The rejection does not damage the record, so the genuine retry still works.",
            wrong="Replaying the old receipt for the conflicting payload would let the client believe 5 was applied when 4 was.",
            verify="Apply `op-10` with 5 after the conflict and confirm the total becomes 9, which shows the rejection did not block new identities.",
        ),
    },
}

for _source in (REASONING, TASK_ANSWERS):
    for _lesson, _tasks in _source.items():
        for _task, _fields in _tasks.items():
            ANSWERS.setdefault(_lesson, {}).setdefault(_task, {}).update(_fields)
