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
      Check(RangeFrom(5, 4).Take(2).SequenceEqual(new[] { 5, 6 }),
            "bounded prefix");
      Check(!RangeFrom(5, 0).Any(), "empty range");
    }
    {
      bool rejected = false;
      try {
        _ = RangeFrom(0, -1);
      } catch (ArgumentOutOfRangeException) {
        rejected = true;
      }
      Check(rejected, "validation occurs at call boundary");
      Check(RangeFrom(2, 3).Sum() == 9, "complete enumeration");
    }
    Console.WriteLine("csharp-022: passed");
    await Task.CompletedTask;
  }

  public static IEnumerable<int> RangeFrom(int start, int count) {
    if (count < 0)
      throw new ArgumentOutOfRangeException(nameof(count));
    return Iterate();
    IEnumerable<int> Iterate() {
      for (int i = 0; i < count; i++)
        yield return checked(start + i);
    }
  }
}
