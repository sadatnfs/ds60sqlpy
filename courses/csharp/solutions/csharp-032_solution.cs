using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Globalization;
using System.Collections.Concurrent;
using System.Threading.Channels;
using System.Net;
using System.Net.Http;
using System.Text.RegularExpressions;
using System.Buffers;

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var result = await ImportAsync(
          "[{\"Name\":\"pear\",\"Quantity\":2},{\"Name\":\"\",\"Quantity\":3}]",
          CancellationToken.None);
      Check(result.Total == 2 && result.Rejected == 1, "validated aggregate");
    }
    {
      using var source = new CancellationTokenSource();
      source.Cancel();
      bool cancelled = false;
      try {
        await ImportAsync("[]", source.Token);
      } catch (OperationCanceledException) {
        cancelled = true;
      }
      Check(cancelled, "cancelled request preserved");
      Check((await ImportAsync("[]", CancellationToken.None)).Total == 0,
            "successful empty report");
    }
    {
      // Task 2: Guided modification
      string pear2 = "{\"Name\":\"pear\",\"Quantity\":2}";
      string pear3 = "{\"Name\":\"pear\",\"Quantity\":3}";
      string json = $"[{pear2},{pear3}]";
      var result = await ImportAsync(json, CancellationToken.None);
      Check(result.Total == 5 && result.Rejected == 0, "quantities summed");
      var items = JsonSerializer.Deserialize<ImportItem[]>(json)!;
      var names = items.Select(item => item.Name);
      int distinct = names.Distinct(StringComparer.Ordinal).Count();
      Check(distinct == 1, "distinct item count is a separate measure");
    }
    {
      // Task 3: Independent construction
      string pear = "{\"Name\":\"pear\",\"Quantity\":2}";
      string blank = "{\"Name\":\"\",\"Quantity\":1}";
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
      Check(rejected == 1, "rejection preserved");
    }
    {
      // Task 5: Boundary evidence
      async Task<string> Outcome(string json) {
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
      Check(await Outcome(fraction) == "malformed", "non-integer quantity");
    }
    Console.WriteLine("csharp-032: passed");
    await Task.CompletedTask;
  }

  public record ImportItem(string Name, int Quantity);
  public record ImportResult(int Total, int Rejected);
  public static async Task<ImportResult> ImportAsync(string json,
                                                     CancellationToken token) {
    token.ThrowIfCancellationRequested();
    var items = JsonSerializer.Deserialize<ImportItem[]>(json) ??
                throw new ArgumentException("array required");
    int total = 0, rejected = 0;
    foreach (var item in items) {
      token.ThrowIfCancellationRequested();
      if (string.IsNullOrWhiteSpace(item.Name) || item.Quantity < 0) {
        rejected++;
        continue;
      }
      total = checked(total + item.Quantity);
    }
    await Task.CompletedTask;
    return new ImportResult(total, rejected);
  }
}
