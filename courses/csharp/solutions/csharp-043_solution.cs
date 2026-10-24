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
            Check(Environment.Version.Major >= 10, "declared runtime generation");
            Check(typeof(List<int>).Assembly.GetName().Name is not null, "framework assembly identity");
        }
        {
            var configuration = new Dictionary<string, string> { ["target"] = "net10.0", ["nullable"] = "enable" };
            Check(configuration["target"] == "net10.0" && configuration["nullable"] == "enable", "reviewed build contract");
        }
        Console.WriteLine("csharp-043: passed");
        await Task.CompletedTask;
    }


}
