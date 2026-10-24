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
      var result = await ImportAsync(
          "[{\"Name\":\"pear\",\"Quantity\":2},{\"Name\":\"\",\"Quantity\":3}]",
          CancellationToken.None);
      Check(result.Total == 2 && result.Rejected == 1, "validated aggregate");
    }
    {
      using var source = new CancellationTokenSource();
      source.Cancel();
      bool cancelled = false;
      try {
        await ImportAsync("[]", source.Token);
      } catch (OperationCanceledException) {
        cancelled = true;
      }
      Check(cancelled, "cancelled request preserved");
      Check((await ImportAsync("[]", CancellationToken.None)).Total == 0,
            "successful empty report");
    }
    Console.WriteLine("csharp-032: passed");
    await Task.CompletedTask;
  }

  public record ImportItem(string Name, int Quantity);
  public record ImportResult(int Total, int Rejected);
  public static async Task<ImportResult> ImportAsync(string json,
                                                     CancellationToken token) {
    token.ThrowIfCancellationRequested();
    var items = JsonSerializer.Deserialize<ImportItem[]>(json) ??
                throw new ArgumentException("array required");
    int total = 0, rejected = 0;
    foreach (var item in items) {
      token.ThrowIfCancellationRequested();
      if (string.IsNullOrWhiteSpace(item.Name) || item.Quantity < 0) {
        rejected++;
        continue;
      }
      total = checked(total + item.Quantity);
    }
    await Task.CompletedTask;
    return new ImportResult(total, rejected);
  }
}
