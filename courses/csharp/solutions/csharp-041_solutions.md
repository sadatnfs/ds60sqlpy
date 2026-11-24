# csharp-041: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-041_solution.cs](csharp-041_solution.cs). It runs both worked examples, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Map a valid request:** The kernel isolates validation and status selection from host configuration. Valid input maps to the created outcome.

**Reject before claiming success:** The response category is part of the public contract and must not disagree with domain acceptance. Invalid requests produce 400 decisions.

## Task answers

### Task 1: Predict and explain

Describe the valid request and its status/body contract.

**Written answer.** `ValidateCreate("pear", 3)` returns `ApiDecision(201, "accepted")`: a nonblank name and a nonnegative quantity. In ApiLab the matching request is `POST /items` with `{"id":"pear-1","name":"pear","quantity":3}`. It answers `201 Created` with `Location: /items/pear-1` and echoes the stored item as JSON.

**Why it is correct.** The status says a resource was created, the Location header says where to fetch it, and the body confirms what was stored. A client can act on all three without guessing.

**Plausible wrong approach.** Returning `200` with the text `accepted` for a create also looks successful, but a client that follows the `Location` header of a 201 has nothing to follow, and the response cannot be told apart from a read.

**How to verify.** The Example A check `result.Status == 201` passes. Against ApiLab, `curl -i` on the POST prints `HTTP/1.1 201 Created` and `Location: /items/pear-1`.

### Task 2: Guided modification

Add a maximum quantity rule and document its rejection.

**Written answer.** Add a branch before the success case: `quantity > 1000 ? new(400, "quantity above 1000")`. Document that 1000 is accepted and 1001 is rejected, and apply the same rule in the ApiLab POST handler so the kernel and the host agree.

**Why it is correct.** An oversized quantity is a client input error, the same category as a negative quantity, so it maps to 400 with a message naming the rule that failed.

**Plausible wrong approach.** Mapping the rule to `413 Payload Too Large` sounds fitting, but 413 describes the size of the request body. A 60-byte JSON body with `quantity: 5000` is not too large, and clients that handle 413 by shrinking uploads would react incorrectly.

**How to verify.** Check `ValidateCreate("pear", 1000).Status == 201` and `ValidateCreate("pear", 1001).Status == 400`, then confirm Example B still passes.

### Task 3: Independent construction

Run the separately prepared ApiLab project and inspect GET and POST responses.

**Written answer.** Copy `fixtures/ApiLab` into an ignored workspace and run `dotnet restore --configfile NuGet.Config`, `dotnet build --no-restore` and `dotnet run --no-build --urls http://127.0.0.1:5080`. In a second terminal, run the six `curl -i` commands from the README.

**Why it is correct.** The six requests cover health, create, read, duplicate create, invalid create and unknown read, so each branch of the handlers in `Program.cs` produces one observed status.

**Plausible wrong approach.** Running `dotnet run` without `--urls` lets the host pick its configured default URL, so the curl commands aimed at port 5080 fail to connect and look like a broken API rather than a different port.

**How to verify.** Expect 200, 201, 200, 409, 400 and 404 in that order. Stop the server with Ctrl+C, start it again, and `GET /items/pear-1` returns 404 because the inventory was in memory.

### Task 4: Diagnose a defect

Diagnose returning 200 before input validation finishes.

**Written answer.** A handler that writes `await context.Response.WriteAsync("ok")` and only then validates has already sent a 200 status line and headers. When validation fails, `context.Response.StatusCode = 400` throws `InvalidOperationException` because the response has started. Validate first, then choose the status, then write the body.

**Why it is correct.** HTTP sends the status before the body. Once `Response.HasStarted` is true, ASP.NET Core cannot change the status, so the decision must be final before any bytes are written.

**Plausible wrong approach.** Catching the `InvalidOperationException` and appending `error` to the body leaves the client with status 200 and a body that disagrees with it. Any client that checks only the status records the invalid item as created.

**How to verify.** Check `context.Response.HasStarted` is false at the point where the status is set. With the kernel, `ValidateCreate` returns its decision before any output, which Example B checks.

### Task 5: Boundary evidence

Test missing identity, zero quantity and unknown resource lookup.

**Written answer.** Missing identity: `ValidateCreate("", 3)` and `ValidateCreate("   ", 3)` return 400. Zero quantity: `ValidateCreate("pear", 0)` returns 201, because the rule is `quantity < 0`. Unknown lookup: the kernel has no lookup, so test ApiLab, where `GET /items/missing` returns 404.

**Why it is correct.** Whitespace-only names are rejected by `string.IsNullOrWhiteSpace`, zero is a real stock level, and a well-formed request for an absent resource is a 404 rather than a client input error.

**Plausible wrong approach.** Writing the rule as `quantity <= 0` rejects an empty bin that the inventory needs to record. Mapping an unknown id to 400 blames the client for a valid request.

**How to verify.** Check the three kernel decisions, then `curl -i http://127.0.0.1:5080/items/missing` prints `HTTP/1.1 404 Not Found`.

### Task 6: Transfer and justify

Design idempotent update behavior and explain how duplicate creation differs.

**Written answer.** Add `PUT /items/{id}` that stores the full representation sent: if the id exists, replace it and return 200; otherwise create it and return 201. Sending the same body twice leaves the same state. `POST /items` stays non-idempotent: in ApiLab the second identical POST returns 409 because `TryAdd` refuses the duplicate.

**Why it is correct.** PUT means the item should now look exactly like this body, so a retried PUT after a timeout is harmless. POST means add one, so the server must detect a repeat.

**Plausible wrong approach.** Implementing PUT as add `quantity` to the stored item makes a retried request after a lost response raise the stock from 3 to 6, which breaks the idempotency that clients and proxies assume for PUT.

**How to verify.** Send the same PUT with quantity 3 twice, then `GET /items/pear-1` shows quantity 3. Repeating the POST gives 201 then 409.

## Mechanism and diagnostic reasoning

An API exposes a contract over a transport. A useful endpoint specifies resource identity, accepted input, status outcomes and response schema. Domain validation must run before a successful status is returned. HTTP method names also communicate semantics: a safe read should not unexpectedly mutate server state.

The browser pad exercises a pure endpoint decision kernel. The checked-in ApiLab fixture supplies a real ASP.NET Core minimal API project using only the shared framework, with an in-memory catalog and explicit validation. It is a separately prepared multi-file workflow, not source accepted by the single Program.cs pad. Running its web host is deliberate and should bind loopback for local learning.

A pure mapping can return a status and body record. In the external project, MapGet and MapPost connect routes to handlers. Results.Ok, BadRequest and NotFound make transport outcomes explicit.

An offline kernel test does not prove endpoint routing, serialization or host startup. The external project intentionally uses in-memory state, so restarting loses its sample inventory. It is not a persistence claim.

## Review before continuing

Run the reference and confirm that it prints `csharp-041: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
