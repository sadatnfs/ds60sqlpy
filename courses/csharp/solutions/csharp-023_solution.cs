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
      int ParseCount(string text) {
        int value = int.Parse(text, CultureInfo.InvariantCulture);
        if (value < 0)
          throw new ArgumentOutOfRangeException(nameof(text));
        return value;
      }
      bool format = false;
      try {
        ParseCount("oops");
      } catch (FormatException) {
        format = true;
      }
      Check(format && ParseCount("3") == 3, "format and success are distinct");
    }
    {
      Exception? observed = null;
      try {
        try {
          throw new IOException("synthetic read failure");
        } catch (IOException cause) {
          throw new InvalidOperationException("import failed", cause);
        }
      } catch (InvalidOperationException error) {
        observed = error;
      }
      Check(observed?.InnerException is IOException, "cause retained");
    }
    {
      // Task 2: Guided modification
      int ParseCount(string text) {
        int value = int.Parse(text, CultureInfo.InvariantCulture);
        if (value < 0)
          throw new ArgumentOutOfRangeException(nameof(text));
        return value;
      }
      string outcome = "none";
      try {
        ParseCount("-2");
      } catch (FormatException) {
        outcome = "format";
      } catch (ArgumentOutOfRangeException) {
        outcome = "negative";
      }
      Check(outcome == "negative", "negative is not a format error");
    }
    {
      // Task 3: Independent construction
      int Import(string text, bool storageAvailable) {
        if (!int.TryParse(text, out int quantity) || quantity < 0) {
          throw new ArgumentException("invalid quantity", nameof(text));
        }
        if (!storageAvailable) {
          throw new IOException("storage unavailable");
        }
        return quantity;
      }
      Check(Import("3", true) == 3, "success");
      string outcome = "none";
      try {
        Import("x", true);
      } catch (ArgumentException) {
        outcome = "invalid input";
      }
      Check(outcome == "invalid input", "input failure");
      try {
        Import("3", false);
      } catch (IOException) {
        outcome = "storage";
      }
      Check(outcome == "storage", "storage failure");
    }
    {
      // Task 5: Boundary evidence
      string Classify(string text) {
        try {
          int value = int.Parse(text, CultureInfo.InvariantCulture);
          return "ok " + value;
        } catch (FormatException) {
          return "rejected";
        }
      }
      Check(Classify("4") == "ok 4", "success");
      Check(Classify("four") == "rejected", "expected rejection");
      bool escaped = false;
      try {
        Classify(null!);
      } catch (ArgumentNullException) {
        escaped = true;
      }
      Check(escaped, "unexpected exception is not swallowed");
    }
    Console.WriteLine("csharp-023: passed");
    await Task.CompletedTask;
  }
}
