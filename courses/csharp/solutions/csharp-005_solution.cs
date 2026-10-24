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
            Check(!(label != null && label.Length > 0), "guarded access");
            label = "ok";
            Check(label != null && label.Length == 2, "present label");
        }
        {
            string Classify(int score) => score switch { < 0 => "invalid", < 60 => "retry", <= 100 => "pass", _ => "invalid" };
            Check(Classify(59) == "retry", "below boundary");
            Check(Classify(60) == "pass", "at boundary");
            Check(Classify(101) == "invalid", "outside domain");
        }
        Console.WriteLine("csharp-005: passed");
        await Task.CompletedTask;
    }


}
