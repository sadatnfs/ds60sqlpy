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
      var counter = new LockedCounter();
      await Task.WhenAll(Enumerable.Range(0, 4).Select(
          _ => Task.Run(() => {
            for (int i = 0; i < 100; i++)
              counter.Add();
          })));
      Check(counter.Value == 400, "all protected increments");
    }
    {
      var account = new LockedCounter();
      account.Add();
      account.Add();
      Check(account.Value == 2, "consistent observation");
      Check(account.Value >= 0, "valid state");
    }
    {
      // Task 2: Guided modification
      var counter = new LockedCounter();
      const int tasks = 8;
      const int perTask = 250;
      void AddMany() {
        for (int i = 0; i < perTask; i++)
          counter.Add();
      }
      var work = new List<Task>();
      for (int t = 0; t < tasks; t++)
        work.Add(Task.Run(AddMany));
      await Task.WhenAll(work);
      Check(counter.Value == tasks * perTask, "exact total 2000");
    }
    {
      // Task 3: Independent construction
      var gate = new Lock();
      int left = 100;
      int right = 0;
      void Transfer(int amount) {
        lock (gate) {
          left -= amount;
          right += amount;
        }
      }
      Task Move() => Task.Run(() => Transfer(5));
      var moves = new List<Task>();
      for (int i = 0; i < 10; i++) {
        moves.Add(Move());
      }
      await Task.WhenAll(moves);
      Check(left + right == 100 && right == 50, "sum preserved");
    }
    {
      // Task 5: Boundary evidence
      var idle = new LockedCounter();
      Check(idle.Value == 0, "zero operations read 0");
      var live = new LockedCounter();
      void Write() {
        for (int i = 0; i < 1000; i++)
          live.Add();
      }
      int Sample() => live.Value;
      var writer = Task.Run(Write);
      var samples = new List<Task<int>>();
      for (int r = 0; r < 4; r++)
        samples.Add(Task.Run(Sample));
      int[] during = await Task.WhenAll(samples);
      await writer;
      Check(during.All(v => v >= 0 && v <= 1000), "each read is a whole count");
      Check(live.Value == 1000, "final total exact");
    }
    Console.WriteLine("csharp-033: passed");
    await Task.CompletedTask;
  }

  public sealed class LockedCounter {
    private readonly Lock gate = new();
    private int value;
    public void Add() { lock (gate) value++; }
    public int Value {
      get { lock (gate) return value; }
    }
  }
}
