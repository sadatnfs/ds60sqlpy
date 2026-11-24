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
      // Task 2: Guided modification
      var utc = TimeSpan.Zero;
      var instant = new DateTimeOffset(2025, 6, 15, 9, 30, 0, utc);
      var service = new StampService(new FixedClock(instant));
      string stamp = service.Stamp("order-7");
      string expected = "2025-06-15T09:30:00.0000000+00:00:order-7";
      Check(stamp == expected, "predicted stamp");
      var epoch = new StampService(new FixedClock(DateTimeOffset.UnixEpoch));
      Check(epoch.Stamp("order-7") != stamp, "only the clock changed");
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
    {
      // Task 5: Boundary evidence
      var utc = TimeSpan.Zero;
      var edge = new DateTimeOffset(2024, 12, 31, 23, 59, 59, utc);
      var service = new StampService(new FixedClock(edge));
      string yearEnd = "2024-12-31T23:59:59.0000000+00:00:a";
      Check(service.Stamp("a") == yearEnd, "year end");
      var next = new StampService(new FixedClock(edge.AddSeconds(1)));
      string newYear = "2025-01-01T00:00:00.0000000+00:00:a";
      Check(next.Stamp("a") == newYear, "next second is next year");
      var plusTwo = edge.ToOffset(TimeSpan.FromHours(2));
      var local = new StampService(new FixedClock(plusTwo));
      string shifted = "2025-01-01T01:59:59.0000000+02:00:a";
      Check(local.Stamp("a") == shifted, "same instant, next date");
      bool Rejects(string id) {
        try {
          service.Stamp(id);
          return false;
        } catch (ArgumentException) {
          return true;
        }
      }
      Check(Rejects("") && Rejects("   "), "blank identity rejected");
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
