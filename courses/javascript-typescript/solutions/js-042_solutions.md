# js-042: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

## Mechanism review

A release is a specific artifact with a reproducible behavior contract, not merely a folder that once worked during development. A small release manifest can name the exact files, record their digests and declare a schema version. Verification should reject unexpected paths before reading files, compare expected byte identities and then execute a bounded smoke test in a fresh process. These checks answer different questions: identity, admissible layout and behavior.

The fixture builds a tiny command-line bundle in an owned temporary directory. Its application has a self-test command and a generic usage failure. The manifest names only app.mjs and package.json, so an altered manifest cannot make the verifier read an arbitrary path. The app's self-test checks real arithmetic behavior and reports the actual Node version. A compatibility gate accepts an explicitly supplied required major version; the course's prepared execution profile remains Node 24. Production policy may pin a full version and image digest rather than only a major.

Observability is part of the output contract. The application emits one result object to stdout and a small completion or failure event to stderr. It does not echo arbitrary command-line values in its error. The caller preserves those channels separately and includes them when a smoke test fails. A successful self-test proves only its covered cases, so the manifest and receipt must not be advertised as production acceptance or exhaustive compatibility.

Maintenance means keeping source, docs, tests, packaged bytes and runtime assumptions aligned. A source edit invalidates a digest and should trigger new execution evidence. Rollback requires retaining a known artifact and its compatible state assumptions; renaming a version label is not a rollback procedure. This lesson performs local packaging and smoke checks only. It does not publish a registry package, deploy a service or change learner state.

**Release artifact:** The exact files intended to be distributed or executed.

**Smoke test:** A small fresh-process check of essential behavior.

**Artifact verification:** Checking allowed layout and expected byte identities.

**Compatibility gate:** An explicit rule comparing observed runtime evidence with release requirements.

## Reading the implementation

The manifest uses an explicit filename allowlist and SHA-256 digests. Paths are rejected before joining them to the bundle directory. The hash list excludes the manifest itself to avoid a self-reference. spawnSync runs the current Node executable with a fixed source path and argument list, bounded timeout and output size. stdout and stderr remain separate. Runtime qualification compares a reported actual major version with a caller-supplied policy rather than trusting package metadata alone.

## Exercise 1: Build, verify and execute a fresh bundle: change one input

Task: In a scratch copy of Example A, change `const result = runBundle(directory, ['--self-test']);` to `const result = runBundle(directory, ['--self-test!']);`. Which check fails, and what value does it see?

The child executes the packaged bytes rather than an already imported development function. The receipt records the runtime that actually ran.

The unchanged code is the exercise block of Example A:

```javascript
await withBundle(async (directory) => {
  await verifyBundle(directory);
  const result = runBundle(directory, ['--self-test']);
  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(result.stdout);
  assert.equal(receipt.checks, 3);
  assert.equal(receipt.status, 'passed');
  assert.equal(receipt.node, process.versions.node);
});
```

**Expected:** The edited run fails with an `AssertionError` at `assert.equal(result.status, 0, result.stderr)`. Restoring `const result = runBundle(directory, ['--self-test']);` brings back: three checks passed; actual Node version reported.

**Verify:** Compare the reported actual and expected values with your prediction, then restore `const result = runBundle(directory, ['--self-test']);`.

## Exercise 2: Reject altered application bytes before execution: debug a regression

Task: A regression made one Example B line read `await appendFile(join(directory, 'app.mjs!'), '\n// controlled tamper fixture\n');`. Locate and repair it without editing the check.

Even a behavior-preserving edit changes artifact identity. The correct repair is to create a new reviewed manifest and rerun evidence, not ignore the mismatch.

The unchanged code is the exercise block of Example B:

```javascript
await withBundle(async (directory) => {
  await appendFile(join(directory, 'app.mjs'), '\n// controlled tamper fixture\n');
  await assert.rejects(verifyBundle(directory), /digest mismatch/u);
});
```

**Expected:** Before the repair the run fails with an `AssertionError` at `assert.rejects(verifyBundle(directory), /digest mismatch/u)`. Restoring `await appendFile(join(directory, 'app.mjs'), '\n// controlled tamper fixture\n');` brings back: digest verification fails.

**Verify:** Keep the failing and repaired runs and name the first value that differs between them.

## Exercise 3: Reject a manifest path outside the allowlist

Task: Replace one file entry with ../outside.txt.

A digest verifier should not treat a manifest as permission to traverse arbitrary files. The supported artifact surface is defined independently of the untrusted filename entry.

```javascript
await withBundle(async (directory) => {
  const path = join(directory, 'manifest.json');
  const manifest = JSON.parse(await readFile(path, 'utf8'));
  manifest.files[0].path = '../outside.txt';
  await writeFile(path, JSON.stringify(manifest));
  await assert.rejects(verifyBundle(directory), /unapproved artifact path/u);
});
```

**Expected:** path is rejected before any outside file is read.

**Verify:** Keep the check `assert.rejects(verifyBundle(directory), /unapproved artifact path/u)`; name an input that would make it fail and the value that changes.

## Exercise 4: Preserve result and diagnostic channels on failure

Task: Invoke an unsupported argument containing a fake secret-like value.

The application reports a useful failure category without reflecting arbitrary arguments. A caller can preserve structured diagnostics without parsing a success-shaped stdout value.

```javascript
await withBundle(async (directory) => {
  const result = runBundle(directory, ['--fixture-secret-value']);
  assert.notEqual(result.status, 0);
  assert.equal(result.stdout, '');
  assert.equal(result.stderr.includes('fixture-secret-value'), false);
  const diagnostic = JSON.parse(result.stderr.trim());
  assert.equal(diagnostic.event, 'usage_error');
});
```

**Expected:** nonzero child exit; stdout empty; generic stderr without the value.

**Verify:** Keep `assert.equal(diagnostic.event, 'usage_error')`. Control: editing it to `assert.equal(diagnostic.event, 'usage_error!');` must make the check fail; then restore it.

## Exercise 5: Derive stable content identity from unchanged files

Task: Read and hash the same app twice and compare with its manifest entry.

The digest is a deterministic function of file bytes. This claim does not imply that independent build systems would emit the same bytes without controlling their own inputs.

```javascript
await withBundle(async (directory) => {
  const bytes = await readFile(join(directory, 'app.mjs'));
  const first = hash(bytes);
  const second = hash(await readFile(join(directory, 'app.mjs')));
  assert.equal(first, second);
  const manifest = JSON.parse(await readFile(join(directory, 'manifest.json'), 'utf8'));
  assert.equal(manifest.files.find((file) => file.path === 'app.mjs').sha256, first);
});
```

**Expected:** equal digests and an unchanged manifest match.

**Verify:** Keep `assert.equal(manifest.files.find((file) => file.path === 'app.mjs').sha256, first)`. Control: editing it to `assert.equal(manifest.files.find(file => file.path !== 'app.mjs').sha256, first);` must make the check fail; then restore it.

## Exercise 6: Gate an observed runtime against explicit policy

Task: Accept the current runtime major for the fixture and reject a different required major.

The example tests the gate's mechanism with an observed value. The actual course policy is supplied by the prepared Node24 profile; accepting a development host in this fixture does not qualify it as that profile.

```javascript
await withBundle(async (directory) => {
  const receipt = JSON.parse(runBundle(directory, ['--self-test']).stdout);
  const actual = Number(process.versions.node.split('.')[0]);
  assert.equal(qualifyRuntime(receipt, actual), true);
  assert.throws(() => qualifyRuntime(receipt, actual + 1), /runtime mismatch/u);
});
```

**Expected:** matching policy passes; mismatched policy throws.

**Verify:** Keep `assert.equal(qualifyRuntime(receipt, actual), true)`. Control: editing it to `assert.equal(qualifyRuntime(receipt, actual), false);` must make the check fail; then restore it.

## After comparison

Fresh case: add `README.txt` to the bundle. Predict the verification result when the manifest lists it but the file is missing, and when the file exists but the manifest omits it. ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
