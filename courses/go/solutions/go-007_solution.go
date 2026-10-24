package main

import (
	"fmt"
	"strings"
	"unicode/utf8"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func main() {
	// Count two units
	{
		text := "A🙂"
		check(len(text) == 5 && utf8.RuneCountInString(text) == 2, "text units")
	}

	// Edit a copied byte slice
	{
		original := "cat"
		data := []byte(original)
		data[0] = 'b'
		check(original == "cat" && string(data) == "bat", "copy edit")
	}

	// Reject malformed encoding
	{
		text := string([]byte{0xff})
		check(!utf8.ValidString(text), "invalid encoding")
	}

	// Slice by rune position
	{
		r := []rune("A🙂")
		check(string(r[1:]) == "🙂", "rune slice")
	}

	// Separate combining forms
	{
		text := "e\u0301"
		check(utf8.RuneCountInString(text) == 2, "combining")
	}

	// Transfer a whitespace policy
	{
		label := strings.TrimSpace(" \tblue sky\n")
		check(label == "blue sky", "trim")
	}
	fmt.Println("All lesson checks passed.")
}
