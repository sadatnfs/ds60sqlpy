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
      var a = DateTimeOffset.Parse("2025-01-01T12:00:00+02:00",
                                   CultureInfo.InvariantCulture);
      var b = DateTimeOffset.Parse("2025-01-01T10:00:00Z",
                                   CultureInfo.InvariantCulture);
      Check(a == b, "same instant");
      Check(a.Offset != b.Offset, "different representations");
    }
    {
      var start = new DateTimeOffset(2025, 1, 1, 0, 0, 0, TimeSpan.Zero);
      var end = start.AddMinutes(90);
      Check((end - start).TotalMinutes == 90, "elapsed duration");
      string encoded = start.ToString("O", CultureInfo.InvariantCulture);
      Check(DateTimeOffset.Parse(encoded, CultureInfo.InvariantCulture) ==
                start,
            "round-trip format");
    }
    Console.WriteLine("csharp-027: passed");
    await Task.CompletedTask;
  }
}
