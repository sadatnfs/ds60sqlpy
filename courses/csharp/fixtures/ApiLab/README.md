# ApiLab: a complete local ASP.NET Core minimal API

This external multi-file lab accompanies csharp-041. It uses the .NET 10 shared web framework and no NuGet packages. The ordinary classroom Program.cs pad does not host this project or expose arbitrary web ports. Use a prepared .NET 10 SDK and a separate terminal in a copied learning directory.

```bash
dotnet restore --configfile NuGet.Config
dotnet build --no-restore
dotnet run --no-build --urls http://127.0.0.1:5080
```

The server deliberately binds loopback. If the port is occupied, choose another unused loopback port and use it consistently. In a second terminal:

```bash
curl -i http://127.0.0.1:5080/health
curl -i -H 'Content-Type: application/json' -d '{"id":"pear-1","name":"pear","quantity":3}' http://127.0.0.1:5080/items
curl -i http://127.0.0.1:5080/items/pear-1
curl -i -H 'Content-Type: application/json' -d '{"id":"pear-1","name":"pear","quantity":3}' http://127.0.0.1:5080/items
curl -i -H 'Content-Type: application/json' -d '{"id":"bad","name":"pear","quantity":-1}' http://127.0.0.1:5080/items
curl -i http://127.0.0.1:5080/items/missing
```

Expected statuses, in order: 200, 201, 200, 409, 400, 404. The duplicate request does not replace the earlier record. ConcurrentDictionary makes the atomic TryAdd admission meaningful under concurrent requests. It does not provide persistence, authentication or a durable transaction log. Restarting this sample intentionally clears its in-memory inventory.

Press Ctrl+C in the server terminal to stop the owned process. Do not stop unrelated services to free the port. Extend this project by injecting the DomainLab core and implementing an explicit persistence adapter. Keep transport errors, validation failures and storage failures distinct. Adding authentication is a separate design, not a production claim conferred by these six HTTP checks.
