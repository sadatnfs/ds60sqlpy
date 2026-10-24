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
            int[] values = { 2, 4, 6, 8 };
            int comparisons = 0;
            bool found = false;
            foreach (int value in values) { comparisons++; if (value == 8) { found = true; break; } }
            Check(found && comparisons == 4, "last-element linear search");
        }
        {
            var index = new HashSet<int>(new[] { 2, 4, 6, 8 });
            Check(index.Contains(8) && !index.Contains(9), "indexed membership");
            Check(index.Count == 4, "index has stored identities");
        }
        Console.WriteLine("csharp-037: passed");
        await Task.CompletedTask;
    }


}
