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
      var rows = new[] { (Kind: "a", Amount: 2), (Kind: "a", Amount: 3),
                         (Kind: "b", Amount: 4) };
      var totals = rows.GroupBy(row => row.Kind)
                       .ToDictionary(group => group.Key,
                                     group => group.Sum(row => row.Amount));
      Check(totals["a"] == 5 && totals["b"] == 4, "one total per kind");
    }
    {
      var left = new[] { (Key: 1, Label: "L") };
      var right = new[] { (Key: 1, Value: "x"), (Key: 1, Value: "y") };
      var joined = left.Join(right, item => item.Key, item => item.Key,
                             (a, b) => a.Label + b.Value)
                       .ToArray();
      Check(joined.SequenceEqual(new[] { "Lx", "Ly" }), "two right matches");
    }
    {
      // Task 2: Guided modification
      var rows = new List<(string Kind, int Amount)> { ("a", 2), ("a", 3) };
      rows.Add(("b", 4));
      rows.Add(("c", 7));
      var groups = rows.GroupBy(row => row.Kind);
      var totals = groups.ToDictionary(g => g.Key, g => g.Sum(r => r.Amount));
      Check(totals.Count == 3 && totals["c"] == 7, "third category");
      int eventTotal = rows.Sum(row => row.Amount);
      Check(eventTotal == 16, "independent event total");
      Check(totals.Values.Sum() == eventTotal, "total conserved");
    }
    {
      // Task 3: Independent construction
      var items = new[] { (Id: 1, Name: "pear"), (Id: 2, Name: "apple") };
      var sales = new[] { (Id: 1, Qty: 2), (Id: 1, Qty: 3), (Id: 2, Qty: 4) };
      var groups = sales.GroupBy(sale => sale.Id);
      var totals = groups.ToDictionary(g => g.Key, g => g.Sum(s => s.Qty));
      var report = items.Select(item => $"{item.Name}={totals[item.Id]}");
      Check(report.SequenceEqual(new[] { "pear=5", "apple=4" }), "joined");
    }
    {
      // Task 5: Boundary evidence
      var names = new Dictionary<int, string>();
      names.Add(1, "pear");
      names.Add(2, "apple");
      var sales = new[] { (Id: 1, Qty: 2), (Id: 3, Qty: 5) };
      var matched = sales.Where(s => names.ContainsKey(s.Id)).ToArray();
      var unmatched = sales.Where(s => !names.ContainsKey(s.Id)).ToArray();
      Check(matched.Length == 1 && names[matched[0].Id] == "pear", "match");
      Check(unmatched.Length == 1 && unmatched[0].Qty == 5, "reported");
      int reported = matched.Sum(s => s.Qty) + unmatched.Sum(s => s.Qty);
      Check(reported == sales.Sum(s => s.Qty), "nothing silently dropped");
    }
    Console.WriteLine("csharp-021: passed");
    await Task.CompletedTask;
  }
}
