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
      var values = new List<int> { 1, 2 };
      var query = values.Where(value => value > 1);
      values.Add(3);
      Check(query.SequenceEqual(new[] { 2, 3 }),
            "query sees later source state");
    }
    {
      var values = new List<int> { 1, 2 };
      int[] snapshot = values.Where(value => value > 1).ToArray();
      values.Add(3);
      Check(snapshot.SequenceEqual(new[] { 2 }), "snapshot remains stable");
      Check(values.Select(value => value * 10).ToArray().Length == 3,
            "projection count");
    }
    {
      // Task 3: Independent construction
      var stock = new Dictionary<string, int> { ["pear"] = 2, ["fig"] = 0 };
      stock["apple"] = 5;
      var kept = stock.Where(row => row.Value > 0);
      var ordered = kept.OrderBy(row => row.Key, StringComparer.Ordinal);
      var report = ordered.Select(row => $"{row.Key}={row.Value}");
      Check(report.SequenceEqual(new[] { "apple=5", "pear=2" }), "report");
    }
    Console.WriteLine("csharp-020: passed");
    await Task.CompletedTask;
  }
}
