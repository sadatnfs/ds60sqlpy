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
      var cases = new[] { (Input: -2, Expected: 0), (Input: 0, Expected: 0),
                          (Input: 3, Expected: 3) };
      foreach (var test in cases)
        Check(ClampNonnegative(test.Input) == test.Expected, "clamp contract");
    }
    {
      int Wrong(int value) => value <= 0 ? 1 : value;
      Check(Wrong(0) != ClampNonnegative(0), "boundary catches wrong default");
      Check(ClampNonnegative(ClampNonnegative(-4)) == ClampNonnegative(-4),
            "idempotence");
    }
    {
      // Task 2: Guided modification
      Check(ClampNonnegative(int.MinValue) == 0, "most negative clamps to 0");
      Check(ClampNonnegative(int.MaxValue) == int.MaxValue, "largest kept");
      bool overflow = false;
      try {
        Math.Abs(int.MinValue);
      } catch (OverflowException) {
        overflow = true;
      }
      Check(overflow, "an Abs-based clamp would fail at the extreme");
    }
    {
      // Task 3: Independent construction
      bool ValidQuantity(int value) => value >= 0 && value <= 1000;
      int[] inputs = { -1, 0, 1000, 1001 };
      bool[] expected = { false, true, true, false };
      for (int i = 0; i < inputs.Length; i++) {
        Check(ValidQuantity(inputs[i]) == expected[i], $"case {inputs[i]}");
      }
    }
    {
      // Task 5: Boundary evidence
      int[] samples = { int.MinValue, -1, 0, 1, int.MaxValue };
      foreach (int value in samples) {
        int once = ClampNonnegative(value);
        Check(ClampNonnegative(once) == once, $"idempotent at {value}");
      }
      Check(ClampNonnegative(-1) == 0, "largest invalid input becomes 0");
      Check(ClampNonnegative(0) == 0, "boundary itself is kept");
      Check(ClampNonnegative(1) == 1, "smallest positive is kept");
    }
    Console.WriteLine("csharp-028: passed");
    await Task.CompletedTask;
  }

  public static int ClampNonnegative(int value) => value < 0 ? 0 : value;
}
