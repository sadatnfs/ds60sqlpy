package main

import (
	"fmt"
	"runtime"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type ServiceState struct {
	Accepting bool
	Active    int
}

func main() {
	// Inspect the current target
	{
		check(runtime.GOOS != "" && runtime.GOARCH != "", "target")
	}

	// Validate a supported deployment tuple
	{
		allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}
		check(allowed["linux/amd64"] && allowed["linux/arm64"], "targets")
	}

	// Refuse an unsupported tuple
	{
		allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}
		check(!allowed["plan9/386"], "unsupported")
	}

	// Model stop-accepting before drain
	{
		s := ServiceState{Accepting: true, Active: 2}
		s.Accepting = false
		check(!s.Accepting && s.Active == 2, "drain start")
		s.Active = 0
		check(!s.Accepting && s.Active == 0, "stopped")
	}

	// Retain unfinished work evidence
	{
		s := ServiceState{Accepting: false, Active: 2}
		s.Active--
		check(s.Active == 1, "unfinished work")
	}

	// Transfer deterministic version metadata
	{
		label := fmt.Sprintf("%s/%s revision=%s", "lesson", "1.0", "abc123")
		check(label == "lesson/1.0 revision=abc123", "version")
	}
	fmt.Println("All lesson checks passed.")
}
