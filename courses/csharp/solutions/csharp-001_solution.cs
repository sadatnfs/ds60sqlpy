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
      string greeting = "Hello, C#";
      Check(greeting.Length == 9, "greeting length");
      Console.WriteLine(greeting);
    }
    {
      int boxes = 3;
      int itemsPerBox = 4;
      int total = boxes * itemsPerBox;
      Check(total == 12, "computed total");
      Check(total != boxes + itemsPerBox, "multiplication is not addition");
    }
    Console.WriteLine("csharp-001: passed");
    await Task.CompletedTask;
  }
}
