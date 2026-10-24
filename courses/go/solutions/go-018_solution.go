package main

import (
	"errors"
	"fmt"
	"io/fs"
	"testing/fstest"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func main() {
	// Read an in-memory file
	{
		files := fstest.MapFS{"data/input.txt": &fstest.MapFile{Data: []byte("red\n")}}
		v, err := fs.ReadFile(files, "data/input.txt")
		check(err == nil && string(v) == "red\n", "file read")
	}

	// Observe a missing file
	{
		_, err := fs.ReadFile(fstest.MapFS{}, "absent.txt")
		check(errors.Is(err, fs.ErrNotExist), "missing file")
	}

	// Reject traversal syntax
	{
		check(!fs.ValidPath("../private") && fs.ValidPath("data/input.txt"), "relative paths")
	}

	// Walk only owned entries
	{
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
	}

	// Separate empty content from absence
	{
		v, err := fs.ReadFile(fstest.MapFS{"empty": &fstest.MapFile{}}, "empty")
		check(err == nil && len(v) == 0, "empty file")
	}

	// Transfer a subtree boundary
	{
		files := fstest.MapFS{"data/item.txt": &fstest.MapFile{Data: []byte("7")}}
		sub, err := fs.Sub(files, "data")
		check(err == nil, "sub root")
		v, err := fs.ReadFile(sub, "item.txt")
		check(err == nil && string(v) == "7", "sub read")
	}
	fmt.Println("All lesson checks passed.")
}
