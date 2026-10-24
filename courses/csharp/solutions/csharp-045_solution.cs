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
            var property = typeof(Metric).GetProperty(nameof(Metric.Count));
            Check(property is not null && property.PropertyType == typeof(int), "known metadata");
            Check(typeof(Metric).GetProperty("Missing") is null, "absent member");
        }
        {
            var metric = new Metric(4);
            Func<Metric, int> getCount = value => value.Count;
            Check(getCount(metric) == 4, "typed projection");
        }
        Console.WriteLine("csharp-045: passed");
        await Task.CompletedTask;
    }

    public record Metric(int Count);
}
