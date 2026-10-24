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
            string? label = null;
            int? length = label?.Length;
            Check(length is null, "absence remains absent");
            Check((length ?? -1) == -1, "explicit display sentinel");
        }
        {
            int? measured = 0;
            int? missing = null;
            Check(measured.HasValue && measured.Value == 0, "valid zero");
            Check(!missing.HasValue, "unknown measurement");
            string Describe(int? value) => value is int actual ? $"measured:{actual}" : "unknown";
            Check(Describe(measured) == "measured:0" && Describe(missing) == "unknown", "preserved meaning");
        }
        Console.WriteLine("csharp-011: passed");
        await Task.CompletedTask;
    }


}
