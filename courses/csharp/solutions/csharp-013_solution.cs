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
            var wallet = new Wallet(10);
            Check(wallet.TrySpend(4) && wallet.Balance == 6, "valid spend");
            Check(!wallet.TrySpend(7) && wallet.Balance == 6, "rejection retains balance");
        }
        {
            var wallet = new Wallet(5);
            bool rejected = false;
            try { wallet.TrySpend(-1); } catch (ArgumentOutOfRangeException) { rejected = true; }
            Check(rejected && wallet.Balance == 5, "malformed input keeps state");
            Check(wallet.TrySpend(0) && wallet.Balance == 5, "zero is allowed");
        }
        Console.WriteLine("csharp-013: passed");
        await Task.CompletedTask;
    }

    public sealed class Wallet { public int Balance { get; private set; } public Wallet(int initial) { if (initial < 0) throw new ArgumentOutOfRangeException(nameof(initial)); Balance = initial; } public bool TrySpend(int amount) { if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount)); if (amount > Balance) return false; Balance -= amount; return true; } }
}
