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
            var counter = new LockedCounter();
            await Task.WhenAll(Enumerable.Range(0, 4).Select(_ => Task.Run(() => { for (int i = 0; i < 100; i++) counter.Add(); })));
            Check(counter.Value == 400, "all protected increments");
        }
        {
            var account = new LockedCounter();
            account.Add(); account.Add();
            Check(account.Value == 2, "consistent observation");
            Check(account.Value >= 0, "valid state");
        }
        Console.WriteLine("csharp-033: passed");
        await Task.CompletedTask;
    }

    public sealed class LockedCounter { private readonly object gate = new(); private int value; public void Add() { lock (gate) value++; } public int Value { get { lock (gate) return value; } } }
}
