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
      var original = new ItemDto("pear", 3);
      string json = JsonSerializer.Serialize(original);
      var restored = JsonSerializer.Deserialize<ItemDto>(json);
      Check(restored == original, "record round trip");
    }
    {
      var invalid = JsonSerializer.Deserialize<ItemDto>(
          "{\"Name\":\"pear\",\"Quantity\":-2}");
      Check(invalid is not null && !Valid(invalid),
            "domain rejection after decoding");
      Check(!Valid(new ItemDto("", 2)), "empty identity rejected");
    }
    Console.WriteLine("csharp-026: passed");
    await Task.CompletedTask;
  }

  public record ItemDto(string Name, int Quantity);
  public static bool
  Valid(ItemDto item) => !string.IsNullOrWhiteSpace(item.Name) && item.Quantity
                                                                      >= 0;
}
