package main

import (
	"errors"
	"fmt"
	"io/fs"
	"os"
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

	// Transfer confinement to a real directory with os.Root
	{
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
	}
	fmt.Println("All lesson checks passed.")
}
