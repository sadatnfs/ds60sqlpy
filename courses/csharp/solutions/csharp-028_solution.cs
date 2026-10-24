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
    Console.WriteLine("csharp-028: passed");
    await Task.CompletedTask;
  }

  public static int ClampNonnegative(int value) => value < 0 ? 0 : value;
}
