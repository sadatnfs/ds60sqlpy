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
      Task<int> pending = Task.FromResult(7);
      int value = await pending;
      Check(value == 7 && pending.IsCompletedSuccessfully,
            "observed completion");
    }
    {
      int[] values = await Task.WhenAll(Task.FromResult(2), Task.FromResult(3));
      Check(values.SequenceEqual(new[] { 2, 3 }), "input order retained");
      bool observed = false;
      try {
        await Task.FromException<int>(new InvalidOperationException("fixture"));
      } catch (InvalidOperationException) {
        observed = true;
      }
      Check(observed, "failure propagated through await");
    }
    Console.WriteLine("csharp-029: passed");
    await Task.CompletedTask;
  }
}
