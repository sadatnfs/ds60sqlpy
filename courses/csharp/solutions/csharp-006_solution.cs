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
    {
      // Task 2: Guided modification
      int[] values = { 2, -3, 4, -1, 6 };
      int sum = 0;
      foreach (int value in values) {
        if (value < 0)
          continue;
        sum += value;
      }
      Check(sum == 12, "negatives skipped");
      Check(sum == values.Where(v => v >= 0).Sum(), "same as filtered sum");
    }
    {
      // Task 3: Independent construction
      bool TryFirstIndex(int[] items, int target, out int index) {
        for (int i = 0; i < items.Length; i++) {
          if (items[i] == target) {
            index = i;
            return true;
          }
        }
        index = -1;
        return false;
      }
      var values = new[] { 5, 7, 7 };
      Check(TryFirstIndex(values, 7, out int at) && at == 1, "first match");
      Check(!TryFirstIndex(values, 9, out _), "not found");
      Check(!TryFirstIndex(Array.Empty<int>(), 1, out _), "empty input");
    }
    {
      // Task 5: Boundary evidence
      int FirstIndex(int[] items, int target) {
        for (int i = 0; i < items.Length; i++) {
          if (items[i] == target)
            return i;
        }
        return -1;
      }
      int[] empty = Array.Empty<int>();
      int[] single = { 4 };
      int[] other = { 1, 2 };
      int[] repeated = { 4, 9, 4 };
      Check(FirstIndex(empty, 4) == -1, "empty input");
      Check(FirstIndex(single, 4) == 0, "singleton match");
      Check(FirstIndex(other, 4) == -1, "no match");
      Check(FirstIndex(repeated, 4) == 0, "repeated match returns the first");
    }
    Console.WriteLine("csharp-006: passed");
    await Task.CompletedTask;
  }
}
