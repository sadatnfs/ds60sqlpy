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
      var result = ValidateCreate("pear", 3);
      Check(result.Status == 201 && result.Message == "accepted",
            "created contract");
    }
    {
      Check(ValidateCreate("", 3).Status == 400, "empty identity");
      Check(ValidateCreate("pear", -1).Status == 400, "negative quantity");
    }
    Console.WriteLine("csharp-041: passed");
    await Task.CompletedTask;
  }

  public record ApiDecision(int Status, string Message);
  public static ApiDecision ValidateCreate(string name, int quantity) =>
      string.IsNullOrWhiteSpace(name) || quantity < 0 ? new(400, "invalid")
                                                      : new(201, "accepted");
}
