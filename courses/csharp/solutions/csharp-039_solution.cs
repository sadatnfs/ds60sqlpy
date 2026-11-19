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
      using var client = new HttpClient(
          new FixtureHandler(HttpStatusCode.OK, "{\"count\":3}"));
      using var response =
          await client.GetAsync("https://example.invalid/count");
      response.EnsureSuccessStatusCode();
      using var json =
          JsonDocument.Parse(await response.Content.ReadAsStringAsync());
      Check(json.RootElement.GetProperty("count").GetInt32() == 3,
            "validated fixture response");
    }
    {
      using var client = new HttpClient(
          new FixtureHandler(HttpStatusCode.ServiceUnavailable, "unavailable"));
      using var response =
          await client.GetAsync("https://example.invalid/count");
      bool rejected = false;
      try {
        response.EnsureSuccessStatusCode();
      } catch (HttpRequestException) {
        rejected = true;
      }
      Check(rejected, "503 is not success");
    }
    {
      // Task 3: Independent construction
      async Task<int> GetCountAsync(HttpClient client, CancellationToken ct) {
        var address = "https://example.invalid/count";
        using var response = await client.GetAsync(address, ct);
        response.EnsureSuccessStatusCode();
        string body = await response.Content.ReadAsStringAsync(ct);
        using var json = JsonDocument.Parse(body);
        return json.RootElement.GetProperty("count").GetInt32();
      }
      var handler = new FixtureHandler(HttpStatusCode.OK, "{\"count\":4}");
      using var client = new HttpClient(handler);
      Check(await GetCountAsync(client, CancellationToken.None) == 4, "count");
    }
    Console.WriteLine("csharp-039: passed");
    await Task.CompletedTask;
  }

  public sealed class FixtureHandler(HttpStatusCode status, string body)
      : HttpMessageHandler {
    protected override Task<HttpResponseMessage>
    SendAsync(HttpRequestMessage request, CancellationToken token) {
      token.ThrowIfCancellationRequested();
      return Task.FromResult(new HttpResponseMessage(
          status) { Content = new StringContent(body) });
    }
  }
}
