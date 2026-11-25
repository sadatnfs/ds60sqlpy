# go-018: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-018_solution.go` implements all six cases.

## Mechanism

A filesystem path is a name interpreted by a filesystem, not proof of ownership or permission. Logical path cleaning removes redundant components but does not prevent symlink escapes or authorize deletion. The io/fs interfaces let programs consume files without depending on a particular disk layout. A deterministic in-memory filesystem makes success, missing-file and malformed-path behavior easy to inspect. When real temporary files are needed, create a unique owned directory, defer its cleanup and never infer ownership from a familiar filename. Persistent learner work belongs in the classroom storage layer; a worker scratch file is temporary and should not be treated as saved progress.

fs.ReadFile accepts an fs.FS and a slash-separated relative path. fs.ValidPath rejects empty paths, leading slashes and dot-dot components under the logical contract. fstest.MapFS provides test files in memory. errors.Is(err, fs.ErrNotExist) detects a missing-file cause across wrapping. filepath.Clean alone is normalization, not a containment security boundary. fs.Sub narrows the names a consumer sees, but its safety depends on the filesystem underneath. For a real directory, os.OpenRoot returns an os.Root whose methods refuse any name that resolves outside that directory, including through symbolic links.

## 1. Read an in-memory file: change one input

Copy worked example 1, change `files := fstest.MapFS{"data/input.txt": &fstest.MapFile{Data: []byte("red\n")}}` to `files := fstest.MapFS{"data/input.txt!": &fstest.MapFile{Data: []byte("red\n")}}` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
files := fstest.MapFS{"data/input.txt": &fstest.MapFile{Data: []byte("red\n")}}
v, err := fs.ReadFile(files, "data/input.txt")
check(err == nil && string(v) == "red\n", "file read")
```

**Expected:** The edited run panics with `file read` because `err == nil && string(v) == "red\n"` no longer holds.

**Verify:** Restoring `files := fstest.MapFS{"data/input.txt": &fstest.MapFile{Data: []byte("red\n")}}` makes the check pass again with the worked observation: the bytes decode to red followed by a newline.

The algorithm uses the same filesystem interface without reaching the host disk. That isolates content behavior from permissions and mount configuration.

## 2. Observe a missing file: debug a regression

Break one line of worked example 2 so `errors.Is(err, fs.ErrNotExist)` fails, then trace the panic back to it.

The unchanged code is worked example 2:

```go
_, err := fs.ReadFile(fstest.MapFS{}, "absent.txt")
check(errors.Is(err, fs.ErrNotExist), "missing file")
```

**Expected:** Your defect panics with `missing file`; undoing it restores the worked observation: the error matches fs.ErrNotExist.

**Verify:** The failing run shows message `missing file`; after the repair `errors.Is(err, fs.ErrNotExist)` holds again.

Preserving a typed cause lets a caller distinguish optional absence from unreadable or malformed content.

## 3. Reject traversal syntax

Validate ../private and data/input.txt.

```go
check(!fs.ValidPath("../private") && fs.ValidPath("data/input.txt"), "relative paths")
```

**Expected:** The traversal path is invalid and the relative data path is valid.

**Verify:** Your solution must keep `!fs.ValidPath("../private") && fs.ValidPath("data/input.txt")` true. Control: changing `check(!fs.ValidPath("../private") && fs.ValidPath("data/input.txt"), "relative paths")` to `check(fs.ValidPath("../private") && fs.ValidPath("data/input.txt"), "relative paths")` panics with message `relative paths`; revert it.

This validates the logical naming grammar. Real disk confinement still needs a filesystem API that safely handles symlinks and concurrent changes.

## 4. Walk only owned entries

Walk a two-file in-memory tree and count regular files.

```go
files := fstest.MapFS{"a.txt": &fstest.MapFile{}, "sub/b.txt": &fstest.MapFile{}}
count := 0
err := fs.WalkDir(files, ".", func(p string, d fs.DirEntry, e error) error {
	if e != nil {
		return e
	}
	if !d.IsDir() {
		count++
	}
	return nil
})
check(err == nil && count == 2, "walk")
```

**Expected:** Exactly two files are observed.

**Verify:** Your solution must keep `err == nil && count == 2` true. Control: changing `if e != nil {` to `if e == nil {` panics with message `walk`; revert it.

The callback must handle the supplied error before dereferencing the entry. Traversal order should not become an accidental business rule.

## 5. Separate empty content from absence

Read an existing zero-byte file.

```go
v, err := fs.ReadFile(fstest.MapFS{"empty": &fstest.MapFile{}}, "empty")
check(err == nil && len(v) == 0, "empty file")
```

**Expected:** Reading succeeds and returns zero bytes.

**Verify:** Your solution must keep `err == nil && len(v) == 0` true. Control: changing `v, err := fs.ReadFile(fstest.MapFS{"empty": &fstest.MapFile{}}, "empty")` to `v, err := fs.ReadFile(fstest.MapFS{"empty!": &fstest.MapFile{}}, "empty")` panics with message `empty file`; revert it.

An empty file and a missing file are different states. Collapsing both into an empty string loses evidence needed for diagnosis.

## 6. Transfer confinement to a real directory with os.Root

Open an owned temporary directory as an os.Root, create item.txt through it, then try to open ../outside.txt through the same root.

```go
dir, err := os.MkdirTemp("", "lesson-root-")
check(err == nil, "owned directory")
defer os.RemoveAll(dir)
root, err := os.OpenRoot(dir)
check(err == nil, "open root")
defer root.Close()
file, err := root.Create("item.txt")
check(err == nil, "create inside")
check(file.Close() == nil, "close")
_, err = root.Open("../outside.txt")
check(err != nil, "escape rejected")
```

**Expected:** item.txt is created inside the root and the escaping name is rejected.

**Verify:** Your solution must keep `err != nil` true. Control: changing `check(err != nil, "escape rejected")` to `check(err == nil, "escape rejected")` panics with message `escape rejected`; revert it.

os.Root, added in Go 1.24, resolves every name beneath the directory it was opened on and refuses names, including symbolic links, that would leave it. fs.ValidPath and fs.Sub only describe names; os.Root enforces confinement on the host filesystem. The deferred RemoveAll releases only the directory this case created.

## Transfer after comparison

Separate three questions whenever a program touches files: is the name syntactically valid, is it confined to the tree the program owns and may the program remove what it created? Later lessons read configuration and fixtures through io/fs and clean up temporary state. Depending on fs.FS instead of the os package also lets tests run against in-memory trees like these.
