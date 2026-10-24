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
            var first = new Person("Ada", 30);
            var second = new Person("Ada", 30);
            Check(first == second, "record value equality");
            Check(!ReferenceEquals(first, second), "distinct objects");
            var older = first with { Age = 31 };
            Check(first.Age == 30 && older.Age == 31, "copy retains prior value");
        }
        {
            var first = new Basket(new List<int> { 1 });
            var second = first with { };
            second.Items.Add(2);
            Check(first.Items.Count == 2, "nested list is shared");
            Check(ReferenceEquals(first.Items, second.Items), "shallow copied member");
        }
        Console.WriteLine("csharp-014: passed");
        await Task.CompletedTask;
    }

    public record Person(string Name, int Age);
    public record Basket(List<int> Items);
}
