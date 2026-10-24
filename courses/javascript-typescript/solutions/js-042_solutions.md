# js-042: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

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

## Exercise 1: Build, verify and execute a fresh bundle

Task: Create the authored bundle, verify hashes and run its self-test in a child.

The child executes the packaged bytes rather than an already imported development function. The receipt records the runtime that actually ran.

```javascript
await withBundle(async directory => {
  await verifyBundle(directory);
  const result = runBundle(directory, ['--self-test']);
  assert.equal(result.status, 0, result.stderr);
  const receipt = JSON.parse(result.stdout);
  assert.equal(receipt.checks, 3);
  assert.equal(receipt.status, 'passed');
  assert.equal(receipt.node, process.versions.node);
});
```

**Expected:** three checks passed; actual Node version reported.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Reject altered application bytes before execution

Task: Append a harmless comment to the owned application after manifest creation.

Even a behavior-preserving edit changes artifact identity. The correct repair is to create a new reviewed manifest and rerun evidence, not ignore the mismatch.

```javascript
await withBundle(async directory => {
  await appendFile(join(directory, 'app.mjs'), '\n// controlled tamper fixture\n');
  await assert.rejects(verifyBundle(directory), /digest mismatch/u);
});
```

**Expected:** digest verification fails.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Reject a manifest path outside the allowlist

Task: Replace one file entry with ../outside.txt.

A digest verifier should not treat a manifest as permission to traverse arbitrary files. The supported artifact surface is defined independently of the untrusted filename entry.

```javascript
await withBundle(async directory => {
  const path = join(directory, 'manifest.json');
  const manifest = JSON.parse(await readFile(path, 'utf8'));
  manifest.files[0].path = '../outside.txt';
  await writeFile(path, JSON.stringify(manifest));
  await assert.rejects(verifyBundle(directory), /unapproved artifact path/u);
});
```

**Expected:** path is rejected before any outside file is read.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Preserve result and diagnostic channels on failure

Task: Invoke an unsupported argument containing a fake secret-like value.

The application reports a useful failure category without reflecting arbitrary arguments. A caller can preserve structured diagnostics without parsing a success-shaped stdout value.

```javascript
await withBundle(async directory => {
  const result = runBundle(directory, ['--fixture-secret-value']);
  assert.notEqual(result.status, 0);
  assert.equal(result.stdout, '');
  assert.equal(result.stderr.includes('fixture-secret-value'), false);
  const diagnostic = JSON.parse(result.stderr.trim());
  assert.equal(diagnostic.event, 'usage_error');
});
```

**Expected:** nonzero child exit; stdout empty; generic stderr without the value.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Derive stable content identity from unchanged files

Task: Read and hash the same app twice and compare with its manifest entry.

The digest is a deterministic function of file bytes. This claim does not imply that independent build systems would emit the same bytes without controlling their own inputs.

```javascript
await withBundle(async directory => {
  const bytes = await readFile(join(directory, 'app.mjs'));
  const first = hash(bytes);
  const second = hash(await readFile(join(directory, 'app.mjs')));
  assert.equal(first, second);
  const manifest = JSON.parse(await readFile(join(directory, 'manifest.json'), 'utf8'));
  assert.equal(manifest.files.find(file => file.path === 'app.mjs').sha256, first);
});
```

**Expected:** equal digests and an unchanged manifest match.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Gate an observed runtime against explicit policy

Task: Accept the current runtime major for the fixture and reject a different required major.

The example tests the gate's mechanism with an observed value. The actual course policy is supplied by the prepared Node24 profile; accepting a development host in this fixture does not qualify it as that profile.

```javascript
await withBundle(async directory => {
  const receipt = JSON.parse(runBundle(directory, ['--self-test']).stdout);
  const actual = Number(process.versions.node.split('.')[0]);
  assert.equal(qualifyRuntime(receipt, actual), true);
  assert.throws(() => qualifyRuntime(receipt, actual + 1), /runtime mismatch/u);
});
```

**Expected:** matching policy passes; mismatched policy throws.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
