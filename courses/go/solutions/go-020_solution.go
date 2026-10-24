package main

import (
	"bytes"
	"encoding/csv"
	"fmt"
	"strconv"
	"strings"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func main() {
	// Parse a quoted comma
	{
		r := csv.NewReader(strings.NewReader("Ada,\"Springfield, West\"\n"))
		v, err := r.Read()
		check(err == nil && len(v) == 2 && v[1] == "Springfield, West", "quoted comma")
	}

	// Reject a ragged row
	{
		r := csv.NewReader(strings.NewReader("a,b,c\n"))
		r.FieldsPerRecord = 2
		_, err := r.Read()
		check(err != nil, "ragged row")
	}

	// Decode a numeric field
	{
		r := csv.NewReader(strings.NewReader("item,12\n"))
		v, err := r.Read()
		check(err == nil, "record")
		n, err := strconv.Atoi(v[1])
		check(err == nil && n == 12, "numeric field")
	}

	// Reject blank numeric content
	{
		_, err := strconv.Atoi("")
		check(err != nil, "blank number")
	}

	// Round-trip a delimiter field
	{
		var b bytes.Buffer
		w := csv.NewWriter(&b)
		check(w.Write([]string{"a,b", "3"}) == nil, "write")
		w.Flush()
		check(w.Error() == nil, "flush")
		v, err := csv.NewReader(&b).Read()
		check(err == nil && v[0] == "a,b", "round trip")
	}

	// Transfer header validation
	{
		v, err := csv.NewReader(strings.NewReader("name,count\n")).Read()
		check(err == nil && len(v) == 2 && v[0] == "name" && v[1] == "count", "header contract")
	}
	fmt.Println("All lesson checks passed.")
}
