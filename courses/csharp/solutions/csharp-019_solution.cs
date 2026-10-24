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
            int factor = 2;
            Func<int, int> scale = value => value * factor;
            Check(scale(3) == 6, "initial capture");
            factor = 4;
            Check(scale(3) == 12, "capture is not frozen");
        }
        {
            var source = new Signal();
            int calls = 0;
            EventHandler handler = (_, _) => calls++;
            source.Raised += handler; source.Emit();
            source.Raised -= handler; source.Emit();
            Check(calls == 1, "unsubscribe ends observation");
        }
        Console.WriteLine("csharp-019: passed");
        await Task.CompletedTask;
    }

    public sealed class Signal { public event EventHandler? Raised; public void Emit() => Raised?.Invoke(this, EventArgs.Empty); }
}
