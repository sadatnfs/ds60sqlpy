package main

import (
	"errors"
	"flag"
	"fmt"
	"io"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func parseArgs(args []string) (int, []string, error) {
	f := flag.NewFlagSet("lesson", flag.ContinueOnError)
	f.SetOutput(io.Discard)
	n := 1
	f.IntVar(&n, "count", 1, "positive count")
	if err := f.Parse(args); err != nil {
		return 0, nil, err
	}
	if n < 1 {
		return 0, nil, errors.New("positive count required")
	}
	return n, f.Args(), nil
}

func main() {
	// Apply an explicit flag
	{
		n, args, err := parseArgs([]string{"-count=3"})
		check(err == nil && n == 3 && len(args) == 0, "flag")
	}

	// Retain a default
	{
		n, _, err := parseArgs(nil)
		check(err == nil && n == 1, "default")
	}

	// Reject an unknown option
	{
		_, _, err := parseArgs([]string{"-mystery=2"})
		check(err != nil, "unknown option")
	}

	// Preserve positional arguments
	{
		_, args, err := parseArgs([]string{"-count=2", "input.csv"})
		check(err == nil && len(args) == 1 && args[0] == "input.csv", "positionals")
	}

	// Reject a domain-invalid count
	{
		_, _, err := parseArgs([]string{"-count=-1"})
		check(err != nil, "range")
	}

	// Transfer precedence
	{
		n, _, err := parseArgs([]string{"-count=4"})
		check(err == nil && n == 4, "precedence")
	}
	fmt.Println("All lesson checks passed.")
}
