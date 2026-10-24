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
            int[] values = { 1, 2, 3 };
            DoubleMiddle(values);
            Check(values.SequenceEqual(new[] { 1, 4, 3 }), "slice aliases array");
        }
        {
            Check(SumDigits("123".AsSpan()) == 6, "digit total");
            Check(SumDigits(ReadOnlySpan<char>.Empty) == 0, "empty identity");
        }
        Console.WriteLine("csharp-035: passed");
        await Task.CompletedTask;
    }

    public static void DoubleMiddle(int[] values) { Span<int> middle = values.AsSpan(1, 1); middle[0] *= 2; }
    public static int SumDigits(ReadOnlySpan<char> text) { int total = 0; foreach (char ch in text) { if (ch < '0' || ch > '9') throw new ArgumentException("digits required"); total += ch - '0'; } return total; }
}
