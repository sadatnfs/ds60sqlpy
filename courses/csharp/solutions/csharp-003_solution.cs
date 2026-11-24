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
    {
      // Task 2: Guided modification
      bool overflowed = false;
      try {
        int small = int.MinValue;
        _ = checked(small - 1);
      } catch (OverflowException) {
        overflowed = true;
      }
      Check(overflowed, "minimum minus one rejected");
      Check(checked(-100 - 20) == -120, "normal subtraction");
    }
    {
      // Task 3: Independent construction
      decimal[] prices = { 19.99m, 5.01m, 0.35m };
      decimal subtotal = prices.Sum();
      decimal tax = subtotal * 0.0825m;
      decimal payable = Math.Round(subtotal + tax, 2, MidpointRounding.ToEven);
      Check(subtotal == 25.35m, "exact decimal subtotal");
      Check(tax == 2.091375m, "unrounded tax");
      Check(payable == 27.44m, "rounded only at the end");
    }
    {
      // Task 5: Boundary evidence
      var even = MidpointRounding.ToEven;
      var away = MidpointRounding.AwayFromZero;
      Check(Math.Round(2.344m, 2, even) == 2.34m, "below, even");
      Check(Math.Round(2.344m, 2, away) == 2.34m, "below, away");
      Check(Math.Round(2.345m, 2, even) == 2.34m, "midpoint, even");
      Check(Math.Round(2.345m, 2, away) == 2.35m, "midpoint, away");
      Check(Math.Round(2.346m, 2, even) == 2.35m, "above, even");
      Check(Math.Round(2.346m, 2, away) == 2.35m, "above, away");
    }
    Console.WriteLine("csharp-003: passed");
    await Task.CompletedTask;
  }
}
