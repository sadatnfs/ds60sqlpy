using System.Collections.Concurrent;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
var items = new ConcurrentDictionary<string, Item>(StringComparer.Ordinal);
app.MapGet("/health", () => Results.Ok(new { status = "ready" }));
app.MapGet("/items", () => Results.Ok(items.Values.OrderBy(item => item.Id, StringComparer.Ordinal).ToArray()));
app.MapGet("/items/{id}", (string id) => items.TryGetValue(id, out Item? item) ? Results.Ok(item) : Results.NotFound());
app.MapPost("/items", (Item item) =>
{
    if (string.IsNullOrWhiteSpace(item.Id) || string.IsNullOrWhiteSpace(item.Name) || item.Quantity < 0)
        return Results.BadRequest(new { error = "nonempty identity/name and nonnegative quantity required" });
    if (!items.TryAdd(item.Id, item)) return Results.Conflict(new { error = "identity already exists" });
    return Results.Created($"/items/{Uri.EscapeDataString(item.Id)}", item);
});
app.Run();

public sealed record Item(string Id, string Name, int Quantity);
