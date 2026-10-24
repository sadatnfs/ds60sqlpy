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
      object value = 12;
      string Describe(object item) =>
          item switch { int number when number >
                            0 => "positive",
                        int => "nonpositive", string { Length : 0 } => "empty",
                        _ => "other" };
      Check(Describe(value) == "positive", "integer branch");
      Check(Describe(-1) == "nonpositive" && Describe("") == "empty",
            "distinct shapes");
    }
    {
      Result success = new Success(8);
      Result failure = new Failure("invalid");
      string Render(Result result) => result switch {
        Success(var count) => $"count:{count}",
        Failure(var reason) => $"error:{reason}",
        _ => throw new InvalidOperationException("unknown result")
      };
      Check(Render(success) == "count:8", "success payload");
      Check(Render(failure) == "error:invalid", "failure payload");
    }
    Console.WriteLine("csharp-015: passed");
    await Task.CompletedTask;
  }

  public abstract record Result;
  public sealed record Success(int Count) : Result;
  public sealed record Failure(string Reason) : Result;
}
