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
            var ledger = new Ledger();
            Check(ledger.Apply("op-1", 3) == 3, "first effect");
            Check(ledger.Apply("op-1", 3) == 3 && ledger.Total == 3, "replayed receipt");
        }
        {
            var ledger = new Ledger();
            ledger.Apply("op-1", 3); ledger.Apply("op-2", 3);
            Check(ledger.Total == 6, "distinct commands");
            bool rejected = false;
            try { ledger.Apply("op-1", 4); } catch (InvalidOperationException) { rejected = true; }
            Check(rejected, "same key cannot change payload");
        }
        Console.WriteLine("csharp-047: passed");
        await Task.CompletedTask;
    }

    public sealed class Ledger { private readonly Dictionary<string, (int Amount, int Result)> results = new(); public int Total { get; private set; } public int Apply(string id, int amount) { if (results.TryGetValue(id, out var prior)) { if (prior.Amount != amount) throw new InvalidOperationException("payload conflict"); return prior.Result; } Total = checked(Total + amount); results.Add(id, (amount, Total)); return Total; } }
}
