package main

import (
	"fmt"
	"path"
	"strconv"
	"strings"
	"unicode"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func main() {
	// Use a package boundary
	{
		check(path.Join("reports", "daily.json") == "reports/daily.json", "path package")
	}

	// Compose standard-library APIs
	{
		v, err := strconv.Atoi(strings.TrimSpace(" 12 "))
		check(err == nil && v == 12, "package composition")
	}

	// Inspect exported spelling
	{
		name := "ParseInt"
		check(unicode.IsUpper([]rune(name)[0]), "export convention")
	}

	// Keep logical imports separate
	{
		check(path.Clean("reports/tmp/../daily") == "reports/daily", "logical clean")
	}

	// Reject malformed input at an API boundary
	{
		_, err := strconv.Atoi(strings.TrimSpace(" none "))
		check(err != nil, "boundary error")
	}

	// Transfer an API contract
	{
		day, err := strconv.Atoi("3")
		check(err == nil && day > 0, "day")
		name := path.Join("reports", fmt.Sprintf("day-%d.json", day))
		check(name == "reports/day-3.json", "report name")
	}
	fmt.Println("All lesson checks passed.")
}
