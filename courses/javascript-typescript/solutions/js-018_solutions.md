# js-018: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

A reliable command-line program has an input contract, an output contract and a failure contract. Arguments select behavior, standard input supplies data, standard output carries machine-readable results, and standard error carries diagnostics. Exit status lets another process distinguish successful completion from invalid input or operational failure without parsing prose. Mixing a friendly banner into JSON stdout can break a downstream consumer even though a human finds the output readable.

The capstone is a small offline order aggregation tool. It accepts only --sum, reads bounded newline-delimited JSON from stdin, validates each row and rejects duplicate ids, then prints one JSON result. Blank lines are ignored under an explicit policy. Quantities and prices use safe integer units. It emits no partial aggregate on an invalid row, so a consumer cannot accidentally use an incomplete result as if it covered all input.

The reference launches the actual CLI as a fresh Node process with fixed arguments, bounded input, a timeout and separate stdout/stderr. All source files live in an owned temporary directory. Tests exercise successful totals, invalid arguments, malformed input, duplicates, empty input and the byte cap. This is a small single-process tool, not a general CSV parser, database transaction or production ingestion service. Later typed and streaming chapters extend the same separation of pure transformation and process I/O.

**CLI contract:** The documented arguments, input format, outputs and exit behavior.

**NDJSON:** One independent JSON value per nonblank line under this fixture policy.

**Failure atomicity:** No partial successful result is exposed when an input fails validation.

**Process boundary:** The interface between a program and its caller through arguments, streams and exit status.

## Reading the implementation

process.argv.slice(2) exposes user arguments after the executable and script paths. for await over process.stdin receives byte chunks. A byte budget is checked before retaining another chunk. Buffer.concat followed by UTF-8 decoding is appropriate only because this fixture enforces a small total input bound. Parsing attaches a one-based line number to validation errors. The program writes its JSON result only after every row passes, and sets process.exitCode on failure so pending diagnostic writes can finish.

## Exercise 1: Aggregate valid rows through a real child process

Task: Send two rows worth 250 and 300 cents to the CLI.

The check uses the actual process contract, not a direct call to an internal aggregate function. Exact separation of result data and diagnostics makes the tool composable with another program.

```javascript
const input = [
  { id: 'A', quantity: 2, priceCents: 125 },
  { id: 'B', quantity: 3, priceCents: 100 },
]
  .map(JSON.stringify)
  .join('\n');
const result = await runCli(['--sum'], input);
assert.equal(result.status, 0, result.stderr);
assert.deepEqual(JSON.parse(result.stdout), { rows: 2, totalCents: 550 });
assert.equal(result.stderr, '');
assert.equal(result.stdout.trim().split('\n').length, 1);
```

**Expected:** exit 0; stdout is exactly one JSON result with 2 rows and 550 cents; stderr empty.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Reject unknown arguments before consuming data

Task: Invoke the tool with --unknown.

A strict argument contract catches misspellings. Silently ignoring an unknown option can make a caller believe an important behavior was enabled when it was not.

```javascript
const result = await runCli(['--unknown'], '');
assert.equal(result.status, 2);
assert.equal(result.stdout, '');
assert.match(result.stderr, /usage/u);
```

**Expected:** exit 2; stdout empty; stderr includes usage.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Report the first invalid row without a partial result

Task: Send a valid first row and malformed JSON on line 2.

The first valid row does not authorize publishing a partial total. The output is committed only after validation of the whole bounded input.

```javascript
const result = await runCli(['--sum'], '{"id":"A","quantity":1,"priceCents":5}\n{broken');
assert.equal(result.status, 2);
assert.equal(result.stdout, '');
assert.match(result.stderr, /line 2/u);
```

**Expected:** exit 2; stdout empty; stderr identifies line 2.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Reject duplicate business identifiers

Task: Send two valid rows with the same id.

Syntactic and numeric validity do not establish uniqueness. A Set records the accepted ids and makes duplicate handling explicit instead of double counting by accident.

```javascript
const row = JSON.stringify({ id: 'A', quantity: 1, priceCents: 5 });
const result = await runCli(['--sum'], row + '\n' + row);
assert.equal(result.status, 2);
assert.equal(result.stdout, '');
assert.match(result.stderr, /duplicate id/u);
```

**Expected:** exit 2 with duplicate id diagnostic.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Define empty input deliberately

Task: Send whitespace and empty lines only.

The empty aggregate follows from the additive identity and the declared blank-line policy. It is not a fallback applied to parse failures, which remain errors.

```javascript
const result = await runCli(['--sum'], '\n  \n');
assert.equal(result.status, 0, result.stderr);
assert.deepEqual(JSON.parse(result.stdout), { rows: 0, totalCents: 0 });
```

**Expected:** exit 0 with rows 0 and totalCents 0.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Enforce an input budget before retaining all data

Task: Send 4097 bytes to a CLI whose cap is 4096.

The budget is measured in bytes at the stream boundary, before concatenation. This caps the fixture input buffer; it does not claim a precise cap on all process memory.

```javascript
const result = await runCli(['--sum'], 'x'.repeat(4097));
assert.equal(result.status, 2);
assert.equal(result.stdout, '');
assert.match(result.stderr, /input limit/u);
```

**Expected:** exit 2 with input limit diagnostic; stdout empty.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
