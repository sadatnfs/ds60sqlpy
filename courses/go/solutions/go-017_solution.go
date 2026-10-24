package main

import (
	"bytes"
	"fmt"
	"io"
	"strings"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func main() {
	// Copy a stream
	{
		var out bytes.Buffer
		n, err := io.Copy(&out, strings.NewReader("alpha"))
		check(err == nil && n == 5 && out.String() == "alpha", "copy")
	}

	// Require a full record
	{
		buf := make([]byte, 4)
		n, err := io.ReadFull(strings.NewReader("ab"), buf)
		check(n == 2 && err == io.ErrUnexpectedEOF, "partial record")
	}

	// Bound visible input
	{
		v, err := io.ReadAll(io.LimitReader(strings.NewReader("abcdef"), 3))
		check(err == nil && string(v) == "abc", "limit")
	}

	// Detect excess data
	{
		v, err := io.ReadAll(io.LimitReader(strings.NewReader("abcd"), 4))
		check(err == nil && len(v) > 3, "excess input")
	}

	// Preserve an empty stream
	{
		var out bytes.Buffer
		n, err := io.Copy(&out, strings.NewReader(""))
		check(err == nil && n == 0 && out.Len() == 0, "empty copy")
	}

	// Transfer exact framing
	{
		r := strings.NewReader("ABxyz")
		h := make([]byte, 2)
		p := make([]byte, 3)
		_, e1 := io.ReadFull(r, h)
		_, e2 := io.ReadFull(r, p)
		check(e1 == nil && e2 == nil && string(h) == "AB" && string(p) == "xyz", "framing")
	}
	fmt.Println("All lesson checks passed.")
}
