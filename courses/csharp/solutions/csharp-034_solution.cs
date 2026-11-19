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
      int count = 0;
      await Task.WhenAll(Enumerable.Range(0, 4).Select(
          _ => Task.Run(() => {
            for (int i = 0; i < 100; i++)
              Interlocked.Increment(ref count);
          })));
      Check(count == 400, "atomic count");
    }
    {
      var counts = new ConcurrentDictionary<string, int>();
      await Task.WhenAll(Enumerable.Range(0, 20).Select(
          _ => Task.Run(() => counts.AddOrUpdate(
                            "a", 1, (_, previous) => previous + 1))));
      Check(counts["a"] == 20, "concurrent key updates");
    }
    {
      // Task 3: Independent construction
      var counts = new ConcurrentDictionary<string, int>();
      string[] words = { "a", "b", "a", "a" };
      int Next(string key, int before) => before + 1;
      Task Add(string w) => Task.Run(() => counts.AddOrUpdate(w, 1, Next));
      await Task.WhenAll(words.Select(Add));
      Check(counts["a"] == 3 && counts["b"] == 1, "concurrent frequencies");
    }
    Console.WriteLine("csharp-034: passed");
    await Task.CompletedTask;
  }
}
