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
            var pattern = new Regex(@"\A[a-z][a-z0-9_]{0,15}\z", RegexOptions.NonBacktracking, TimeSpan.FromSeconds(1));
            Check(pattern.IsMatch("report_2"), "accepted identifier");
            Check(!pattern.IsMatch("2report") && !pattern.IsMatch("report!"), "rejected shapes");
        }
        {
            string literal = "a+b";
            var pattern = new Regex(@"\A" + Regex.Escape(literal) + @"\z", RegexOptions.NonBacktracking, TimeSpan.FromSeconds(1));
            Check(pattern.IsMatch("a+b") && !pattern.IsMatch("aaab"), "escaped literal");
        }
        Console.WriteLine("csharp-038: passed");
        await Task.CompletedTask;
    }


}
