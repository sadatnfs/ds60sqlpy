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
    Console.WriteLine("csharp-021: passed");
    await Task.CompletedTask;
  }
}
