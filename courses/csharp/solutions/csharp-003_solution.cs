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
      bool overflowed = false;
      try {
        int large = int.MaxValue;
        _ = checked(large + 1);
      } catch (OverflowException) {
        overflowed = true;
      }
      Check(overflowed, "overflow must be visible");
      Check(checked(100 + 20) == 120, "normal addition");
    }
    {
      decimal amount = 0.1m + 0.2m;
      Check(amount == 0.3m, "decimal tenths");
      Check(Math.Round(2.345m, 2, MidpointRounding.ToEven) == 2.34m,
            "even midpoint");
      Check(Math.Round(2.345m, 2, MidpointRounding.AwayFromZero) == 2.35m,
            "away midpoint");
    }
    Console.WriteLine("csharp-003: passed");
    await Task.CompletedTask;
  }
}
