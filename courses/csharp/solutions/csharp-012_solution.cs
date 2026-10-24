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
            var first = new Point(2, 3);
            var second = first;
            second.X = 9;
            Check(first.X == 2 && second.X == 9, "struct copy");
        }
        {
            var first = new Counter();
            var second = first;
            second.Value++;
            Check(first.Value == 1, "shared mutation");
            Check(ReferenceEquals(first, second), "same object");
        }
        Console.WriteLine("csharp-012: passed");
        await Task.CompletedTask;
    }

    public struct Point { public int X; public int Y; public Point(int x, int y) { X = x; Y = y; } }
    public sealed class Counter { public int Value { get; set; } }
}
