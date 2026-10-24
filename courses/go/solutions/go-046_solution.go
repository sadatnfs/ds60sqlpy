package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type Decision struct {
	UID         string
	Allowed     bool
	Reason      string
	SideEffects int
}

func admit(uid string, replicas, maximum int, dryRun bool) Decision {
	d := Decision{UID: uid}
	if uid == "" {
		d.Reason = "request UID required"
		return d
	}
	if replicas < 0 || replicas > maximum {
		d.Reason = "replicas outside allowed range"
		return d
	}
	d.Allowed = true
	return d
}

func main() {
	// Accept a valid range
	{
		d := admit("r1", 3, 5, false)
		check(d.Allowed && d.UID == "r1", "allow")
	}

	// Reject a negative value
	{
		d := admit("r2", -1, 5, false)
		check(!d.Allowed && d.Reason != "", "negative")
	}

	// Check the exact upper boundary
	{
		check(admit("r3", 5, 5, false).Allowed && !admit("r4", 6, 5, false).Allowed, "boundary")
	}

	// Preserve request identity
	{
		d := admit("request-42", 2, 5, false)
		check(d.UID == "request-42", "UID")
	}

	// Keep dry-run side effects absent
	{
		d := admit("r5", 2, 5, true)
		check(d.Allowed && d.SideEffects == 0, "dry run")
	}

	// Transfer missing identity refusal
	{
		d := admit("", 2, 5, false)
		check(!d.Allowed, "missing UID")
	}
	fmt.Println("All lesson checks passed.")
}
