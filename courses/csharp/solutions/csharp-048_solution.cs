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
      var report =
          Report(new[] { new Row("b", 2), new Row("a", 3), new Row("b", 4) });
      Check(report.Text == "a=3;b=6" && report.Rejected == 0, "stable report");
    }
    {
      var report =
          Report(new[] { new Row("", 2), new Row("a", -1), new Row("b", 0) });
      Check(report.Text == "b=0" && report.Rejected == 2,
            "zero differs from rejected");
      Check(Report(Array.Empty<Row>()).Text == "", "empty input");
    }
    Console.WriteLine("csharp-048: passed");
    await Task.CompletedTask;
  }

  public record Row(string Name, int Quantity);
  public static (string Text, int Rejected) Report(IEnumerable<Row> rows) {
    var valid = new List<Row>();
    int rejected = 0;
    foreach (var row in rows) {
      if (string.IsNullOrWhiteSpace(row.Name) || row.Quantity < 0)
        rejected++;
      else
        valid.Add(row);
    }
    string text = string.Join(
        ";", valid.GroupBy(row => row.Name)
                 .OrderBy(group => group.Key, StringComparer.Ordinal)
                 .Select(group => group.Key + "=" +
                                  group.Sum(row => row.Quantity)
                                      .ToString(CultureInfo.InvariantCulture)));
    return (text, rejected);
  }
}
