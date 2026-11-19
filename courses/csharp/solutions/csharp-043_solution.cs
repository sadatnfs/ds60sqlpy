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
      Check(Environment.Version.Major >= 10, "declared runtime generation");
      Check(typeof(List<int>).Assembly.GetName().Name is not null,
            "framework assembly identity");
    }
    {
      string? target = AppContext.TargetFrameworkName;
      Check(target == ".NETCoreApp,Version=v10.0", "compiled target framework");
      Check(Environment.Version.Major == 10, "running runtime generation");
    }
    Console.WriteLine("csharp-043: passed");
    await Task.CompletedTask;
  }
}
