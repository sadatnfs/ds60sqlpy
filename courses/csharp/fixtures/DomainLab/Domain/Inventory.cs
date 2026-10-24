namespace Journey.Domain;

public sealed record Item(string Name, int Quantity);
public sealed record Report(IReadOnlyDictionary<string, int> Totals,
                            int Rejected);

public static class Inventory {
  public static Report Summarize(IEnumerable<Item> items) {
    ArgumentNullException.ThrowIfNull(items);
    var totals = new SortedDictionary<string, int>(StringComparer.Ordinal);
    int rejected = 0;
    foreach (Item item in items) {
      if (string.IsNullOrWhiteSpace(item.Name) || item.Quantity < 0) {
        rejected++;
        continue;
      }
      totals.TryGetValue(item.Name, out int previous);
      totals[item.Name] = checked(previous + item.Quantity);
    }
    return new Report(
        new System.Collections.ObjectModel.ReadOnlyDictionary<string, int>(
            totals),
        rejected);
  }
}
