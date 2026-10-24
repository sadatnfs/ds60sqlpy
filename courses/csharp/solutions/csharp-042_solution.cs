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
            var rights = new HashSet<string>(StringComparer.Ordinal) { "report:read" };
            Check(rights.Contains("report:read"), "allowed action");
            Check(!rights.Contains("report:delete"), "unlisted action denied");
        }
        {
            string Redact(string key, string value) => key.Equals("token", StringComparison.OrdinalIgnoreCase) ? "[redacted]" : value;
            Check(Redact("TOKEN", "synthetic-secret") == "[redacted]", "secret omitted");
            Check(Redact("status", "failed") == "failed", "useful nonsecret context retained");
        }
        Console.WriteLine("csharp-042: passed");
        await Task.CompletedTask;
    }


}
