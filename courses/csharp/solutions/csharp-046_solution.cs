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
      int[] values = [1, 2, 3];
      List<int> list = [..values, 4];
      Check(list.SequenceEqual(new[] { 1, 2, 3, 4 }), "collection spread");
    }
    {
      var scale = new Scale(3);
      Check(scale.Apply(4) == 12, "primary constructor parameter");
      Check(nameof(List<>) == "List", "C# 14 unbound generic nameof");
      StringBuilder? missing = null;
      missing?.Capacity = 32;
      Check(missing is null, "C# 14 null-conditional assignment");
      Check("\e" == "\u001b", "C# 13 escape sequence");
    }
    {
      // Task 2: Guided modification
      List<int> none = [];
      int[] empty = [];
      Check(none.Count == 0 && empty.Length == 0, "both empty");
      Check(empty.GetType() == typeof(int[]), "target decides the type");
      none.Add(1);
      Check(none.Count == 1, "the empty list is a new mutable list");
      IEnumerable<int> view = [];
      Check(!view.Any(), "interface target is also empty");
    }
    {
      // Task 5: Boundary evidence
      int[] nothing = [];
      List<int> spread = [..nothing];
      Check(spread.Count == 0, "empty spread adds nothing");
      List<int> mixed = [0, ..nothing, 9];
      Check(mixed.SequenceEqual(new[] { 0, 9 }), "neighbors kept");
      var zero = new Scale(0);
      Check(zero.Apply(5) == 0, "zero scaling");
      Check(zero.Apply(int.MaxValue) == 0, "zero cannot overflow");
    }
    Console.WriteLine("csharp-046: passed");
    await Task.CompletedTask;
  }

  public sealed class Scale(int factor) {
    public int Apply(int value) => checked(value * factor);
  }
}
