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

internal static class Program {
  private static void Check(bool condition, string reason) {
    if (!condition)
      throw new InvalidOperationException(reason);
  }

  private static async Task Main() {
    {
      var channel = Channel.CreateBounded<int>(1);
      Check(channel.Writer.TryWrite(4), "first item admitted");
      Check(!channel.Writer.TryWrite(5), "capacity reached");
      Check(await channel.Reader.ReadAsync() == 4, "admitted value retained");
    }
    {
      var channel = Channel.CreateBounded<int>(2);
      channel.Writer.TryWrite(2);
      channel.Writer.TryWrite(3);
      channel.Writer.Complete();
      int sum = 0;
      await foreach (int value in channel.Reader.ReadAllAsync()) sum += value;
      await channel.Reader.Completion;
      Check(sum == 5 && !channel.Writer.TryWrite(9), "drained and closed");
    }
    {
      // Task 2: Guided modification
      var channel = Channel.CreateBounded<int>(3);
      var admitted = new List<bool>();
      for (int i = 1; i <= 4; i++)
        admitted.Add(channel.Writer.TryWrite(i));
      Check(admitted.SequenceEqual(new[] { true, true, true, false }), "cap 3");
      Check(channel.Reader.Count == 3, "three items buffered");
      Check(await channel.Reader.ReadAsync() == 1, "oldest item first");
    }
    {
      // Task 3: Independent construction
      var channel = Channel.CreateBounded<int>(2);
      Task producer = Task.Run(async () => {
        for (int i = 1; i <= 5; i++) {
          await channel.Writer.WriteAsync(i);
        }
        channel.Writer.Complete();
      });
      int sum = 0;
      int count = 0;
      await foreach (int value in channel.Reader.ReadAllAsync()) {
        sum += value;
        count++;
      }
      await producer;
      Check(sum == 15 && count == 5, "every item consumed once");
    }
    {
      // Task 5: Boundary evidence
      var empty = Channel.CreateBounded<int>(2);
      empty.Writer.Complete();
      int seen = 0;
      await foreach (int value in empty.Reader.ReadAllAsync()) { seen++; }
      await empty.Reader.Completion;
      Check(seen == 0, "completed empty channel ends at once");
      var full = Channel.CreateBounded<int>(2);
      full.Writer.TryWrite(7);
      full.Writer.TryWrite(8);
      Check(!full.Writer.TryWrite(9), "buffer full");
      full.Writer.Complete();
      int sum = 0;
      await foreach (int value in full.Reader.ReadAllAsync()) { sum += value; }
      await full.Reader.Completion;
      Check(sum == 15, "full buffer drained after completion");
    }
    Console.WriteLine("csharp-031: passed");
    await Task.CompletedTask;
  }
}
