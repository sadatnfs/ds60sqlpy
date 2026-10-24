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
      int[] source = { 2, 4 };
      int[] alias = source;
      int[] copy = (int[])source.Clone();
      alias[0] = 9;
      Check(source[0] == 9 && copy[0] == 2, "alias versus copy");
    }
    {
      int[,] grid = { { 1, 2, 3 }, { 4, 5, 6 } };
      Check(grid.GetLength(0) == 2 && grid.GetLength(1) == 3,
            "rectangular shape");
      int sum = 0;
      for (int row = 0; row < grid.GetLength(0); row++)
        for (int col = 0; col < grid.GetLength(1); col++)
          sum += grid[row, col];
      Check(sum == 21, "all six cells");
    }
    Console.WriteLine("csharp-008: passed");
    await Task.CompletedTask;
  }
}
