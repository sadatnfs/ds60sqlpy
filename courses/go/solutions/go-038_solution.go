package main

import (
	"errors"
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

var ErrConflict = errors.New("conflict")

type Versioned struct {
	Value   int
	Version string
}

func versionUpdate(s *Versioned, observed string, value int, next string) error {
	if s.Version != observed {
		return ErrConflict
	}
	s.Value = value
	s.Version = next
	return nil
}

func main() {
	// Accept a current version
	{
		s := Versioned{Value: 2, Version: "a"}
		err := versionUpdate(&s, "a", 3, "b")
		check(err == nil && s.Value == 3 && s.Version == "b", "current update")
	}

	// Reject a stale version
	{
		s := Versioned{Value: 3, Version: "b"}
		err := versionUpdate(&s, "a", 9, "c")
		check(errors.Is(err, ErrConflict) && s.Value == 3, "conflict")
	}

	// Reread before retry
	{
		s := Versioned{Value: 4, Version: "b"}
		observed := s
		check(versionUpdate(&s, observed.Version, observed.Value+1, "c") == nil && s.Value == 5, "reread")
	}

	// Keep opaque tokens opaque
	{
		s := Versioned{Value: 1, Version: "rv:opaque"}
		check(versionUpdate(&s, "rv:opaque", 2, "next:opaque") == nil, "opaque")
	}

	// Retain another field
	{
		labels := map[string]string{"owner": "other"}
		s := Versioned{Value: 1, Version: "x"}
		check(versionUpdate(&s, "x", 2, "y") == nil && labels["owner"] == "other", "field scope")
	}

	// Transfer bounded conflict handling
	{
		s := Versioned{Value: 3, Version: "new"}
		conflicts := 0
		for i := 0; i < 2; i++ {
			if errors.Is(versionUpdate(&s, "old", 9, "unused"), ErrConflict) {
				conflicts++
			}
		}
		check(conflicts == 2 && s.Value == 3, "stale retries")
	}
	fmt.Println("All lesson checks passed.")
}
