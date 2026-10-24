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
            var channel = Channel.CreateBounded<int>(1);
            Check(channel.Writer.TryWrite(4), "first item admitted");
            Check(!channel.Writer.TryWrite(5), "capacity reached");
            Check(await channel.Reader.ReadAsync() == 4, "admitted value retained");
        }
        {
            var channel = Channel.CreateBounded<int>(2);
            channel.Writer.TryWrite(2); channel.Writer.TryWrite(3); channel.Writer.Complete();
            int sum = 0;
            await foreach (int value in channel.Reader.ReadAllAsync()) sum += value;
            await channel.Reader.Completion;
            Check(sum == 5 && !channel.Writer.TryWrite(9), "drained and closed");
        }
        Console.WriteLine("csharp-031: passed");
        await Task.CompletedTask;
    }


}
