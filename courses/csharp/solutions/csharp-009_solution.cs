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
            var values = new List<int>(10);
            Check(values.Count == 0 && values.Capacity >= 10, "capacity is not count");
            values.Add(3); values.Add(5);
            Check(values.Count == 2 && values[1] == 5, "append order");
        }
        {
            var values = new List<int> { -1, 2, -3, 4 };
            int[] before = values.ToArray();
            int removed = values.RemoveAll(value => value < 0);
            Check(removed == 2 && values.SequenceEqual(new[] { 2, 4 }), "filtered mutation");
            Check(before.Length == 4, "snapshot retained");
        }
        Console.WriteLine("csharp-009: passed");
        await Task.CompletedTask;
    }


}
