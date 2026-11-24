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
      Task<int> pending = Task.FromResult(7);
      int value = await pending;
      Check(value == 7 && pending.IsCompletedSuccessfully,
            "observed completion");
    }
    {
      int[] values = await Task.WhenAll(Task.FromResult(2), Task.FromResult(3));
      Check(values.SequenceEqual(new[] { 2, 3 }), "input order retained");
      bool observed = false;
      try {
        await Task.FromException<int>(new InvalidOperationException("fixture"));
      } catch (InvalidOperationException) {
        observed = true;
      }
      Check(observed, "failure propagated through await");
    }
    {
      // Task 2: Guided modification
      var tasks =
          new[] { Task.FromResult(5), Task.FromResult(1), Task.FromResult(3) };
      int[] values = await Task.WhenAll(tasks);
      Check(values.SequenceEqual(new[] { 5, 1, 3 }), "input order kept");
      Check(tasks.All(task => task.IsCompletedSuccessfully), "all completed");
    }
    {
      // Task 3: Independent construction
      async Task<int> TotalAsync(IEnumerable<Task<int>> parts) {
        int[] values = await Task.WhenAll(parts);
        if (values.Any(value => value < 0)) {
          throw new ArgumentException("negative part");
        }
        return values.Sum();
      }
      var parts = new[] { Task.FromResult(2), Task.FromResult(5) };
      Check(await TotalAsync(parts) == 7, "validated total");
    }
    {
      // Task 5: Boundary evidence
      int[] ok = await Task.WhenAll(Task.FromResult(1), Task.FromResult(2));
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
      Check(none.Length == 0, "empty input completes with no values");
    }
    Console.WriteLine("csharp-029: passed");
    await Task.CompletedTask;
  }
}
