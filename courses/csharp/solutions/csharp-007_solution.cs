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
      int Double(int value) => checked(value * 2);
      int original = 7;
      int result = Double(original);
      Check(result == 14 && original == 7, "input value is retained");
      Check(Double(0) == 0, "zero case");
    }
    {
      int DivideExact(int value, int divisor) {
        if (divisor == 0 || value % divisor != 0)
          throw new ArgumentException("exact nonzero divisor required");
        return value / divisor;
      }
      Check(DivideExact(12, 3) == 4, "exact quotient");
      bool rejected = false;
      try {
        _ = DivideExact(7, 2);
      } catch (ArgumentException) {
        rejected = true;
      }
      Check(rejected, "fractional quotient rejected");
    }
    {
      // Task 2: Guided modification
      int Triple(int value) => checked(value * 3);
      Check(Triple(0) == 0, "zero stays zero");
      Check(Triple(-4) == -12, "negative input keeps its sign");
      Check(Triple(5) == 15, "positive input");
    }
    {
      // Task 3: Independent construction
      int Area(int width, int height) {
        if (width < 0 || height < 0) {
          throw new ArgumentOutOfRangeException(nameof(width));
        }
        return checked(width * height);
      }
      Check(Area(3, 4) == 12 && Area(0, 9) == 0, "valid dimensions");
      bool rejected = false;
      try {
        Area(-1, 2);
      } catch (ArgumentOutOfRangeException) {
        rejected = true;
      }
      Check(rejected, "negative dimension rejected");
    }
    {
      // Task 5: Boundary evidence
      int DivideExact(int value, int divisor) {
        if (divisor == 0)
          throw new DivideByZeroException();
        if (value % divisor != 0)
          throw new ArgumentException("not an exact quotient");
        return value / divisor;
      }
      bool zeroRejected = false;
      try {
        DivideExact(6, 0);
      } catch (DivideByZeroException) {
        zeroRejected = true;
      }
      bool remainderRejected = false;
      try {
        DivideExact(7, 2);
      } catch (ArgumentException) {
        remainderRejected = true;
      }
      Check(zeroRejected, "zero divisor has its own failure");
      Check(remainderRejected, "remainder has its own failure");
      Check(DivideExact(-12, 3) == -4, "exact negative quotient");
    }
    Console.WriteLine("csharp-007: passed");
    await Task.CompletedTask;
  }
}
