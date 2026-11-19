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
      int factor = 2;
      Func<int, int> scale = value => value * factor;
      Check(scale(3) == 6, "initial capture");
      factor = 4;
      Check(scale(3) == 12, "capture is not frozen");
    }
    {
      var source = new Signal();
      int calls = 0;
      EventHandler handler = (_, _) => calls++;
      source.Raised += handler;
      source.Emit();
      source.Raised -= handler;
      source.Emit();
      Check(calls == 1, "unsubscribe ends observation");
    }
    {
      // Task 3: Independent construction
      int[] Transform(int[] values, Func<int, int> change) {
        var result = new int[values.Length];
        for (int i = 0; i < values.Length; i++) {
          result[i] = change(values[i]);
        }
        return result;
      }
      int[] input = { 1, 2, 3 };
      int[] scaled = Transform(input, value => value * 10);
      Check(scaled.SequenceEqual(new[] { 10, 20, 30 }), "delegate applied");
      Check(input[0] == 1, "input unchanged");
    }
    Console.WriteLine("csharp-019: passed");
    await Task.CompletedTask;
  }

  public sealed class Signal {
    public event EventHandler? Raised;
    public void Emit() => Raised?.Invoke(this, EventArgs.Empty);
  }
}
