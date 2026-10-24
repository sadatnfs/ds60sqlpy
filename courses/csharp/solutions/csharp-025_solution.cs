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
      string root = Path.Combine(Path.GetTempPath(),
                                 "lesson-" + Guid.NewGuid().ToString("N"));
      Directory.CreateDirectory(root);
      try {
        string path = Path.Combine(root, "note.txt");
        File.WriteAllText(path, "café", Encoding.UTF8);
        Check(File.ReadAllText(path, Encoding.UTF8) == "café",
              "UTF-8 round trip");
      } finally {
        Directory.Delete(root, true);
      }
      Check(!Directory.Exists(root), "owned cleanup");
    }
    {
      string fileName = "report.csv";
      Check(Path.GetFileName(fileName) == fileName, "simple leaf name");
      Check(Path.GetFileName("nested/report.csv") != "nested/report.csv",
            "nested name is not a leaf");
      Check(Path.GetExtension(fileName) == ".csv", "extension classification");
    }
    Console.WriteLine("csharp-025: passed");
    await Task.CompletedTask;
  }
}
