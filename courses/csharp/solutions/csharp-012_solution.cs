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
      var first = new Point(2, 3);
      var second = first;
      second.X = 9;
      Check(first.X == 2 && second.X == 9, "struct copy");
    }
    {
      var first = new Counter();
      var second = first;
      second.Value++;
      Check(first.Value == 1, "shared mutation");
      Check(ReferenceEquals(first, second), "same object");
    }
    {
      // Task 2: Guided modification
      var first = new Counter();
      first.Value = 5;
      var second = new Counter();
      second.Value = 5;
      Check(first.Value == second.Value, "equal property values");
      Check(!ReferenceEquals(first, second), "separate identities");
      Check(!first.Equals(second), "class Equals defaults to identity");
      second.Value++;
      Check(first.Value == 5 && second.Value == 6, "independent state");
    }
    {
      // Task 3: Independent construction
      var coordinate = new Point(1, 2);
      var moved = coordinate;
      moved.X = 5;
      var session = new Counter();
      var sameSession = session;
      sameSession.Value = 3;
      Check(coordinate.X == 1 && moved.X == 5, "coordinate copied by value");
      Check(session.Value == 3, "session shared by reference");
    }
    {
      // Task 5: Boundary evidence
      var original = (Count: 1, Items: new List<int> { 1 });
      var copy = original;
      copy.Count = 2;
      copy.Items.Add(2);
      Check(original.Count == 1, "value field copied");
      Check(original.Items.Count == 2, "list content shared");
      Check(ReferenceEquals(original.Items, copy.Items), "same list object");
    }
    Console.WriteLine("csharp-012: passed");
    await Task.CompletedTask;
  }

  public struct Point {
    public int X;
    public int Y;
    public Point(int x, int y) {
      X = x;
      Y = y;
    }
  }
  public sealed class Counter {
    public int Value { get; set; }
  }
}
