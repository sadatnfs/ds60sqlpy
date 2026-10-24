package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type Lease struct {
	Holder  string
	Expires int
}

func acquire(l *Lease, candidate string, now, duration int) bool {
	if candidate == "" || duration <= 0 {
		return false
	}
	if l.Holder != "" && l.Holder != candidate && now < l.Expires {
		return false
	}
	l.Holder = candidate
	l.Expires = now + duration
	return true
}

func main() {
	// Acquire an empty lease
	{
		l := Lease{}
		check(acquire(&l, "a", 10, 5) && l.Holder == "a" && l.Expires == 15, "acquire")
	}

	// Reject a competing candidate
	{
		l := Lease{Holder: "a", Expires: 15}
		check(!acquire(&l, "b", 12, 5) && l.Holder == "a", "contender")
	}

	// Renew current leadership
	{
		l := Lease{Holder: "a", Expires: 15}
		check(acquire(&l, "a", 13, 5) && l.Expires == 18, "renew")
	}

	// Take over after expiry
	{
		l := Lease{Holder: "a", Expires: 15}
		check(acquire(&l, "b", 15, 5) && l.Holder == "b", "takeover")
	}

	// Reject a stale fenced operation
	{
		current := 5
		accept := func(token int) bool { return token == current }
		check(!accept(4) && accept(5), "fencing")
	}

	// Transfer invalid-duration refusal
	{
		l := Lease{}
		check(!acquire(&l, "a", 10, 0) && l.Holder == "", "duration")
	}
	fmt.Println("All lesson checks passed.")
}
