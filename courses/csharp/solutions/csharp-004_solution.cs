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
      string original = "data";
      string changed = original.ToUpperInvariant();
      Check(original == "data" && changed == "DATA", "strings are unchanged");
      Check(string.Equals("KEY", "key", StringComparison.OrdinalIgnoreCase),
            "identifier comparison");
    }
    {
      string symbol = "😀";
      Check(symbol.Length == 2, "UTF-16 units");
      Check(symbol.EnumerateRunes().Count() == 1, "Unicode scalar");
      Check(Encoding.UTF8.GetByteCount(symbol) == 4, "UTF-8 bytes");
    }
    {
      // Task 2: Guided modification
      string Label(int count) {
        string unit = count == 1 ? "file" : "files";
        return $"{count} {unit}";
      }
      Check(Label(3) == "3 files", "plural label");
      Check(Label(1) == "1 file", "singular label");
      Check(Label(0) == "0 files", "zero uses the plural");
    }
    {
      // Task 3: Independent construction
      bool SameKey(string left, string right) {
        return string.Equals(left, right, StringComparison.OrdinalIgnoreCase);
      }
      Check(SameKey("Report-ID", "report-id"), "case-insensitive match");
      Check(!SameKey("report-id", "report_id"), "different characters differ");
      Check(SameKey("i", "I"), "ordinal policy, no culture rules");
    }
    {
      // Task 5: Boundary evidence
      string ascii = "A";
      string emoji = "\U0001F600";
      string accented = "e\u0301";
      int Elements(string text) => new StringInfo(text).LengthInTextElements;
      Check(ascii.Length == 1 && Elements(ascii) == 1, "ASCII");
      Check(emoji.Length == 2 && Elements(emoji) == 1, "emoji");
      Check(accented.Length == 2 && Elements(accented) == 1, "combining mark");
      Check(accented.EnumerateRunes().Count() == 2, "two scalars");
    }
    Console.WriteLine("csharp-004: passed");
    await Task.CompletedTask;
  }
}
