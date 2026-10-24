package main

import (
	"bytes"
	"crypto/subtle"
	"fmt"
	"html/template"
	"net/url"
	"path/filepath"
	"strings"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func main() {
	// Escape HTML data
	{
		var b bytes.Buffer
		t := template.Must(template.New("x").Parse("<p>{{.}}</p>"))
		check(t.Execute(&b, "<script>alert(1)</script>") == nil, "render")
		check(strings.Contains(b.String(), "&lt;script&gt;"), "escape")
	}

	// Encode a query value
	{
		original := "a&role=admin"
		encoded := url.QueryEscape(original)
		decoded, err := url.QueryUnescape(encoded)
		check(err == nil && decoded == original && encoded != original, "query")
	}

	// Reject traversal grammar
	{
		check(!filepath.IsLocal("../outside") && filepath.IsLocal("reports/item.txt"), "local path")
	}

	// Apply a byte budget
	{
		check(len([]byte("abc")) <= 4 && len([]byte("abcde")) > 4, "budget")
	}

	// Compare fixed-size values
	{
		check(subtle.ConstantTimeCompare([]byte("abcd"), []byte("abcd")) == 1, "equal")
		check(subtle.ConstantTimeCompare([]byte("abcd"), []byte("abce")) == 0, "different")
	}

	// Transfer a reviewed action set
	{
		allowed := map[string]bool{"read": true, "list": true}
		check(allowed["read"] && !allowed["exec"], "allowlist")
	}
	fmt.Println("All lesson checks passed.")
}
