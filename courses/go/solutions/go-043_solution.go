package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func finalAction(deleting, hasFinalizer, cleaned, owned bool) string {
	if !owned {
		return "ownership-error"
	}
	if !deleting {
		if !hasFinalizer {
			return "add-finalizer"
		}
		return "reconcile"
	}
	if !hasFinalizer {
		return "done"
	}
	if !cleaned {
		return "cleanup"
	}
	return "remove-own-finalizer"
}

func main() {
	// Register cleanup responsibility
	{
		check(finalAction(false, false, false, true) == "add-finalizer", "register")
	}

	// Retain a healthy object
	{
		check(finalAction(false, true, false, true) == "reconcile", "normal")
	}

	// Clean before releasing deletion
	{
		check(finalAction(true, true, false, true) == "cleanup", "cleanup")
	}

	// Remove only after success
	{
		check(finalAction(true, true, true, true) == "remove-own-finalizer", "release")
	}

	// Refuse ownership mismatch
	{
		check(finalAction(true, true, false, false) == "ownership-error", "UID mismatch")
	}

	// Transfer preservation of other finalizers
	{
		values := []string{"lesson.example/cleanup", "other.example/retain"}
		out := []string{}
		for _, v := range values {
			if v != "lesson.example/cleanup" {
				out = append(out, v)
			}
		}
		check(len(out) == 1 && out[0] == "other.example/retain", "preserve others")
	}
	fmt.Println("All lesson checks passed.")
}
