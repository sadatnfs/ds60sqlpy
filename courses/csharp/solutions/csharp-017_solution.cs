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
            IRate rate = new FlatRate(3);
            Check(rate.Cost(4) == 12, "flat rate");
            Check(Total(rate, 0) == 0, "consumer uses contract");
        }
        {
            IRate rate = new CappedRate(3, 10);
            Check(Total(rate, 4) == 10, "capped policy");
            Check(Total(new FlatRate(3), 4) == 12, "same consumer, different policy");
        }
        Console.WriteLine("csharp-017: passed");
        await Task.CompletedTask;
    }

    public interface IRate { int Cost(int units); }
    public sealed record FlatRate(int Price) : IRate { public int Cost(int units) => checked(Price * units); }
    public sealed record CappedRate(int Price, int Cap) : IRate { public int Cost(int units) => Math.Min(checked(Price * units), Cap); }
    public static int Total(IRate rate, int units) => rate.Cost(units);
}
