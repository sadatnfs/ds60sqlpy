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
            int[] rented = ArrayPool<int>.Shared.Rent(3);
            try { rented[0] = 2; rented[1] = 3; rented[2] = 4; Check(rented.AsSpan(0, 3).ToArray().Sum() == 9, "logical range"); Check(rented.Length >= 3, "minimum capacity"); }
            finally { ArrayPool<int>.Shared.Return(rented, clearArray: true); }
        }
        {
            var retained = new List<byte[]> { new byte[32], new byte[32] };
            Check(retained.Count == 2, "references retained");
            retained.Clear();
            Check(retained.Count == 0, "application releases references");
        }
        Console.WriteLine("csharp-036: passed");
        await Task.CompletedTask;
    }


}
