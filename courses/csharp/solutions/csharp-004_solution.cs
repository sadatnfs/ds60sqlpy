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
            string original = "data";
            string changed = original.ToUpperInvariant();
            Check(original == "data" && changed == "DATA", "strings are unchanged");
            Check(string.Equals("KEY", "key", StringComparison.OrdinalIgnoreCase), "identifier comparison");
        }
        {
            string symbol = "😀";
            Check(symbol.Length == 2, "UTF-16 units");
            Check(symbol.EnumerateRunes().Count() == 1, "Unicode scalar");
            Check(Encoding.UTF8.GetByteCount(symbol) == 4, "UTF-8 bytes");
        }
        Console.WriteLine("csharp-004: passed");
        await Task.CompletedTask;
    }


}
