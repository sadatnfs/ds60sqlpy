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
            var resource = new Probe();
            using (resource) { Check(!resource.Closed, "open inside scope"); }
            Check(resource.Closed, "closed after scope");
        }
        {
            var resource = new Probe();
            try { using (resource) { throw new InvalidOperationException("fixture"); } }
            catch (InvalidOperationException) { }
            Check(resource.Closed, "exception still cleans up");
        }
        Console.WriteLine("csharp-024: passed");
        await Task.CompletedTask;
    }

    public sealed class Probe : IDisposable { public bool Closed { get; private set; } public void Dispose() { Closed = true; } }
}
