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
      using var source = new CancellationTokenSource();
      source.Cancel();
      bool observed = false;
      try {
        source.Token.ThrowIfCancellationRequested();
      } catch (OperationCanceledException) {
        observed = true;
      }
      Check(observed, "cooperative observation");
    }
    {
      var completion = new TaskCompletionSource<int>(
          TaskCreationOptions.RunContinuationsAsynchronously);
      using var source = new CancellationTokenSource();
      source.Cancel();
      bool cancelled = false;
      try {
        await completion.Task.WaitAsync(source.Token);
      } catch (OperationCanceledException) {
        cancelled = true;
      }
      Check(cancelled && !completion.Task.IsCompleted, "only the wait ended");
      completion.SetResult(9);
      Check(await completion.Task == 9, "underlying result still arrives");
    }
    {
      // Task 2: Guided modification
      var state = new List<string>();
      using var source = new CancellationTokenSource();
      void Apply(string change, CancellationToken token) {
        token.ThrowIfCancellationRequested();
        state.Add(change);
      }
      Apply("first", source.Token);
      source.Cancel();
      bool stopped = false;
      try {
        Apply("second", source.Token);
      } catch (OperationCanceledException) {
        stopped = true;
      }
      Check(stopped && state.SequenceEqual(new[] { "first" }), "no change");
    }
    {
      // Task 3: Independent construction
      var committed = new List<int>();
      using var source = new CancellationTokenSource();
      void Process(int[] items, CancellationToken token) {
        foreach (int item in items) {
          token.ThrowIfCancellationRequested();
          committed.Add(item);
          if (item == 2) {
            source.Cancel();
          }
        }
      }
      bool stopped = false;
      try {
        Process(new[] { 1, 2, 3 }, source.Token);
      } catch (OperationCanceledException) {
        stopped = true;
      }
      Check(stopped && committed.SequenceEqual(new[] { 1, 2 }), "kept work");
    }
    {
      // Task 5: Boundary evidence
      int runs = 0;
      void Work(CancellationToken token) {
        token.ThrowIfCancellationRequested();
        runs++;
      }
      using var early = new CancellationTokenSource();
      early.Cancel();
      bool refused = false;
      try {
        Work(early.Token);
      } catch (OperationCanceledException) {
        refused = true;
      }
      Check(refused && runs == 0, "cancelled before start: no work");
      using var late = new CancellationTokenSource();
      Work(late.Token);
      late.Cancel();
      Check(runs == 1, "cancellation after completion undoes nothing");
      var finished = Task.FromResult(4);
      Check(await finished.WaitAsync(late.Token) == 4, "completed result kept");
    }
    Console.WriteLine("csharp-030: passed");
    await Task.CompletedTask;
  }
}
