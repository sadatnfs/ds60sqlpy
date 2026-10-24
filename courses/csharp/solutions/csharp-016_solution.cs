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

internal static class Program
{
    private static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
    }

    private static async Task Main()
    {
        {
            var totals = Import(new[] { "pear,2", "apple,3", "pear,4" });
            Check(totals.Rejected == 0, "all accepted");
            Check(totals.Counts["pear"] == 6 && totals.Counts["apple"] == 3, "per-item totals");
        }
        {
            var totals = Import(new[] { "pear,2", "pear,no", "apple,-1", "broken" });
            Check(totals.Rejected == 3, "rejections counted");
            Check(totals.Counts.Count == 1 && totals.Counts["pear"] == 2, "only valid data contributes");
            Check(Import(Array.Empty<string>()).Counts.Count == 0, "empty input");
        }
        Console.WriteLine("csharp-016: passed");
        await Task.CompletedTask;
    }

    public static (Dictionary<string, int> Counts, int Rejected) Import(IEnumerable<string> lines) { var counts = new Dictionary<string, int>(StringComparer.Ordinal); int rejected = 0; foreach (string line in lines) { string[] fields = line.Split(','); if (fields.Length != 2 || string.IsNullOrWhiteSpace(fields[0]) || !int.TryParse(fields[1], out int quantity) || quantity < 0) { rejected++; continue; } counts.TryGetValue(fields[0], out int before); counts[fields[0]] = checked(before + quantity); } return (counts, rejected); }
}
