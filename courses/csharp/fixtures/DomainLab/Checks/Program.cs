using Journey.Domain;

static void Check(bool condition, string reason) {
  if (!condition)
    throw new InvalidOperationException(reason);
}

Report report = Inventory.Summarize([
  new("pear", 2), new("apple", 3), new("pear", 4), new("", 9), new("apple", -1)
]);
Check(report.Totals["pear"] == 6, "duplicate names aggregate");
Check(report.Totals["apple"] == 3, "invalid rows do not alter totals");
Check(report.Rejected == 2, "rejected records are accounted for");
Check(report.Totals.Keys.SequenceEqual(["apple", "pear"]),
      "report ordering is ordinal");
Check(Inventory.Summarize([]).Totals.Count == 0, "empty input stays empty");
Check(Inventory.Summarize([new("zero", 0)]).Totals.ContainsKey("zero"),
      "present zero is preserved");
bool overflow = false;
try {
  Inventory.Summarize([new("large", int.MaxValue), new("large", 1)]);
} catch (OverflowException) {
  overflow = true;
}
Check(overflow, "overflow is visible");
Console.WriteLine("DomainLab: seven contract checks passed");
