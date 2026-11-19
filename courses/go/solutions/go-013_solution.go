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
		exported := func(name string) bool { return name != "" && unicode.IsUpper([]rune(name)[0]) }
		check(exported("ParseInt") && !exported("parseInt") && !exported(""), "export convention")
	}

	// Read the go and toolchain directives
	{
		mod := "module example.org/learning/report\n\ngo 1.27\n\ntoolchain go1.27.3\n"
		directives := map[string]string{}
		for _, line := range strings.Split(mod, "\n") {
			fields := strings.Fields(line)
			if len(fields) == 2 {
				directives[fields[0]] = fields[1]
			}
		}
		check(directives["module"] == "example.org/learning/report" && directives["go"] == "1.27" && directives["toolchain"] == "go1.27.3", "directives")
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
