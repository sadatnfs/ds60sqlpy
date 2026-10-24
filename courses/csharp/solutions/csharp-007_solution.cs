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
            int Double(int value) => checked(value * 2);
            int original = 7;
            int result = Double(original);
            Check(result == 14 && original == 7, "input value is retained");
            Check(Double(0) == 0, "zero case");
        }
        {
            int DivideExact(int value, int divisor) { if (divisor == 0 || value % divisor != 0) throw new ArgumentException("exact nonzero divisor required"); return value / divisor; }
            Check(DivideExact(12, 3) == 4, "exact quotient");
            bool rejected = false;
            try { _ = DivideExact(7, 2); } catch (ArgumentException) { rejected = true; }
            Check(rejected, "fractional quotient rejected");
        }
        Console.WriteLine("csharp-007: passed");
        await Task.CompletedTask;
    }


}
