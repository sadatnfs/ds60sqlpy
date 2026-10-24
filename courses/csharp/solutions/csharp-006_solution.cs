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
      int[] values = { 2, 4, 6 };
      int sum = 0;
      foreach (int value in values)
        sum += value;
      Check(sum == 12, "sum of all values");
      Check(Array.Empty<int>().Sum() == 0, "empty sum identity");
    }
    {
      int[] values = { 3, 8, 8 };
      int found = -1;
      for (int i = 0; i < values.Length; i++) {
        if (values[i] == 8) {
          found = i;
          break;
        }
      }
      Check(found == 1, "first matching position");
      Check(!Array.Exists(values, value => value == 9), "absent target");
    }
    Console.WriteLine("csharp-006: passed");
    await Task.CompletedTask;
  }
}
