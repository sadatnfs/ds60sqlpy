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
            int larger = Max(4, 9);
            string later = Max("apple", "pear");
            Check(larger == 9 && later == "pear", "generic comparison");
        }
        {
            var pair = new Pair<string>("left", "right");
            Check(pair.Swap() == new Pair<string>("right", "left"), "swapped pair");
            Check(Max(5, 5) == 5, "tie case");
        }
        Console.WriteLine("csharp-018: passed");
        await Task.CompletedTask;
    }

    public static T Max<T>(T left, T right) where T : IComparable<T> => left.CompareTo(right) >= 0 ? left : right;
    public record Pair<T>(T First, T Second) { public Pair<T> Swap() => new(Second, First); }
}
