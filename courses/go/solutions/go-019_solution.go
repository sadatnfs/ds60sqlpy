package main

import (
	"encoding/json"
	"fmt"
	"io"
	"strings"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type Config struct {
	Name  string `json:"name"`
	Count int    `json:"count"`
}

func main() {
	// Decode a typed object
	{
		var c Config
		err := json.Unmarshal([]byte(`{"name":"sample","count":3}`), &c)
		check(err == nil && c.Name == "sample" && c.Count == 3, "typed JSON")
	}

	// Reject an unknown property
	{
		var c Config
		d := json.NewDecoder(strings.NewReader(`{"name":"x","extra":1}`))
		d.DisallowUnknownFields()
		check(d.Decode(&c) != nil, "unknown field")
	}

	// Detect a second document
	{
		d := json.NewDecoder(strings.NewReader(`{} {}`))
		var a, b any
		check(d.Decode(&a) == nil && d.Decode(&b) == nil, "trailing document")
	}

	// Confirm exact completion
	{
		d := json.NewDecoder(strings.NewReader(`{"name":"x"}`))
		var c Config
		check(d.Decode(&c) == nil, "first decode")
		var extra any
		check(d.Decode(&extra) == io.EOF, "exact end")
	}

	// Preserve a large integer token
	{
		d := json.NewDecoder(strings.NewReader(`9007199254740993`))
		d.UseNumber()
		var v any
		check(d.Decode(&v) == nil && v.(json.Number).String() == "9007199254740993", "number token")
	}

	// Transfer domain validation
	{
		var c Config
		err := json.Unmarshal([]byte(`{"name":"x","count":-1}`), &c)
		check(err == nil && c.Count < 0, "domain invalid")
	}
	fmt.Println("All lesson checks passed.")
}
