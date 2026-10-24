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
            using var source = new CancellationTokenSource();
            source.Cancel();
            bool observed = false;
            try { source.Token.ThrowIfCancellationRequested(); } catch (OperationCanceledException) { observed = true; }
            Check(observed, "cooperative observation");
        }
        {
            var completion = new TaskCompletionSource<int>(TaskCreationOptions.RunContinuationsAsynchronously);
            using var source = new CancellationTokenSource(); source.Cancel();
            bool cancelled = false;
            try { await completion.Task.WaitAsync(source.Token); } catch (OperationCanceledException) { cancelled = true; }
            Check(cancelled && !completion.Task.IsCompleted, "only the wait ended");
            completion.SetResult(9);
            Check(await completion.Task == 9, "underlying result still arrives");
        }
        Console.WriteLine("csharp-030: passed");
        await Task.CompletedTask;
    }


}
