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
            int whole = 7 / 2;
            double fraction = (double)7 / 2;
            Check(whole == 3, "integer division");
            Check(fraction == 3.5, "floating division");
        }
        {
            bool accepted = int.TryParse("42", out int value);
            bool rejected = int.TryParse("forty-two", out _);
            Check(accepted && value == 42, "valid count");
            Check(!rejected, "invalid count is not zero");
        }
        Console.WriteLine("csharp-002: passed");
        await Task.CompletedTask;
    }


}
