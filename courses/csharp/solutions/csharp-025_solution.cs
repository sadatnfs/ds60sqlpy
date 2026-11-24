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
      var utf8 = new UTF8Encoding(false);
      try {
        string path = Path.Combine(root, "note.txt");
        File.WriteAllText(path, "café", utf8);
        Check(File.ReadAllBytes(path).Length == 5, "five UTF-8 bytes, no BOM");
        Check(File.ReadAllText(path, utf8) == "café", "UTF-8 round trip");
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
    {
      // Task 2: Guided modification
      string id = Guid.NewGuid().ToString("N");
      string folder = Path.Combine(Path.GetTempPath(), "lines-" + id);
      Directory.CreateDirectory(folder);
      try {
        string path = Path.Combine(folder, "lines.txt");
        string text = "first\nsecond\n";
        File.WriteAllText(path, text, new UTF8Encoding(false));
        Check(File.ReadAllBytes(path).Length == 13, "13 bytes with two LF");
        string read = File.ReadAllText(path);
        Check(read == text && !read.Contains('\r'), "LF policy preserved");
        var lines = File.ReadAllLines(path);
        Check(lines.Length == 2 && lines[1] == "second", "two lines");
      } finally {
        Directory.Delete(folder, true);
      }
    }
    {
      // Task 3: Independent construction
      string name = "inventory-" + Guid.NewGuid().ToString("N");
      string folder = Path.Combine(Path.GetTempPath(), name);
      Directory.CreateDirectory(folder);
      try {
        string path = Path.Combine(folder, "report.txt");
        string report = "pear: 3\napple: 5";
        File.WriteAllText(path, report, Encoding.UTF8);
        Check(File.ReadAllText(path, Encoding.UTF8) == report, "round trip");
      } finally {
        Directory.Delete(folder, true);
      }
      Check(!Directory.Exists(folder), "temporary folder removed");
    }
    {
      // Task 5: Boundary evidence
      string id = Guid.NewGuid().ToString("N");
      string folder = Path.Combine(Path.GetTempPath(), "text-" + id);
      Directory.CreateDirectory(folder);
      var utf8 = new UTF8Encoding(false);
      try {
        string empty = Path.Combine(folder, "empty.txt");
        File.WriteAllText(empty, "", utf8);
        Check(new FileInfo(empty).Length == 0, "empty file has no bytes");
        Check(File.ReadAllText(empty, utf8) == "", "empty round trip");
        string named = Path.Combine(folder, "names.txt");
        string text = "Zoë, Łódź, 東京";
        File.WriteAllText(named, text, utf8);
        Check(text.Length == 13, "13 UTF-16 code units");
        Check(new FileInfo(named).Length == 21, "21 UTF-8 bytes");
        Check(File.ReadAllText(named, utf8) == text, "non-ASCII round trip");
      } finally {
        Directory.Delete(folder, true);
      }
    }
    Console.WriteLine("csharp-025: passed");
    await Task.CompletedTask;
  }
}
