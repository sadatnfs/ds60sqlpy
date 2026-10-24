# DomainLab: a real two-project .NET application

This is a separately prepared project lab for csharp-043 and csharp-048. It is not accepted by the single-file classroom pad. Use a prepared .NET 10 SDK on Linux, WSL 2 or another supported SDK host. The project has no third-party packages and its NuGet configuration disables remote sources.

Copy this directory into your own ignored learning workspace before editing. From that copied directory:

```bash
dotnet --version
dotnet restore Checks/Checks.csproj --configfile NuGet.Config
dotnet build Checks/Checks.csproj --no-restore
dotnet run --project Checks/Checks.csproj --no-build
```

Expect `DomainLab: seven contract checks passed`. A failed contract throws and exits unsuccessfully. Restore establishes framework asset files; build compiles the library and executable; run executes the compiled checks. Successful restore alone proves neither compilation nor behavior.

`Domain/Inventory.cs` owns validation and aggregation. `Checks/Program.cs` owns independently derived examples, including empty input, duplicate identities, valid zero, rejection accounting and overflow. The read-only dictionary wrapper prevents a consumer from mutating the returned dictionary through its exposed interface. Item records are immutable.

Try adding per-item rejection reasons without putting console I/O into the domain library. Then add a report renderer in the executable. Preserve the existing cases and explain which new misconception each additional test rejects.

For a deployment experiment, run `dotnet publish Checks/Checks.csproj -c Release -o publish` inside your copied lab. That output is framework-dependent by default. A self-contained or Native AOT publish requires an explicit target architecture and additional preparation. Do not infer that it runs on every OS from one successful build.
