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
            int[] values = [1, 2, 3];
            List<int> list = [.. values, 4];
            Check(list.SequenceEqual(new[] { 1, 2, 3, 4 }), "collection spread");
        }
        {
            var scale = new Scale(3);
            Check(scale.Apply(4) == 12, "primary constructor parameter");
            Check(nameof(Scale.Apply) == "Apply", "symbol name");
        }
        Console.WriteLine("csharp-046: passed");
        await Task.CompletedTask;
    }

    public sealed class Scale(int factor) { public int Apply(int value) => checked(value * factor); }
}
