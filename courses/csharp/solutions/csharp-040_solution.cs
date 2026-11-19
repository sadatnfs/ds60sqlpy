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
      var service = new StampService(new FixedClock(
          new DateTimeOffset(2025, 1, 1, 0, 0, 0, TimeSpan.Zero)));
      Check(
          service.Stamp("a").StartsWith("2025-01-01", StringComparison.Ordinal),
          "fixed time");
    }
    {
      var service = new StampService(new FixedClock(DateTimeOffset.UnixEpoch));
      bool rejected = false;
      try {
        service.Stamp("");
      } catch (ArgumentException) {
        rejected = true;
      }
      Check(rejected, "domain rejects empty identity");
    }
    {
      // Task 3: Independent construction
      (int Total, int Rejected) Aggregate(IEnumerable<int> quantities) {
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
      Check(result.Total == 5 && result.Rejected == 1, "core aggregation");
    }
    Console.WriteLine("csharp-040: passed");
    await Task.CompletedTask;
  }

  public interface IClock {
    DateTimeOffset Now { get; }
  }
  public sealed record FixedClock(DateTimeOffset Now) : IClock;
  public sealed class StampService(IClock clock) {
    public string Stamp(string id) {
      if (string.IsNullOrWhiteSpace(id))
        throw new ArgumentException("identity required");
      return clock.Now.ToString("O", CultureInfo.InvariantCulture) + ":" + id;
    }
  }
}
