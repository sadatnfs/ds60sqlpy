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
            int ParseCount(string text) { int value = int.Parse(text, CultureInfo.InvariantCulture); if (value < 0) throw new ArgumentOutOfRangeException(nameof(text)); return value; }
            bool format = false;
            try { ParseCount("oops"); } catch (FormatException) { format = true; }
            Check(format && ParseCount("3") == 3, "format and success are distinct");
        }
        {
            Exception? observed = null;
            try { try { throw new IOException("synthetic read failure"); } catch (IOException cause) { throw new InvalidOperationException("import failed", cause); } }
            catch (InvalidOperationException error) { observed = error; }
            Check(observed?.InnerException is IOException, "cause retained");
        }
        Console.WriteLine("csharp-023: passed");
        await Task.CompletedTask;
    }


}
