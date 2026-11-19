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

func (s *ServiceState) Admit() bool {
	if !s.Accepting {
		return false
	}
	s.Active++
	return true
}
func (s *ServiceState) Drain() { s.Accepting = false }
func (s *ServiceState) Finish() {
	if s.Active > 0 {
		s.Active--
	}
}

func main() {
	// Inspect the current target
	{
		check(runtime.GOOS != "" && runtime.GOARCH != "", "target")
	}

	// Validate the running deployment tuple
	{
		allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}
		target := runtime.GOOS + "/" + runtime.GOARCH
		check(allowed[target], "running target")
	}

	// Refuse an unsupported tuple
	{
		allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}
		supported := func(goos, goarch string) bool { return allowed[goos+"/"+goarch] }
		check(!supported("plan9", "386") && !supported("linux", "") && supported("linux", "arm64"), "unsupported")
	}

	// Model stop-accepting before drain
	{
		s := ServiceState{Accepting: true, Active: 2}
		s.Drain()
		check(!s.Admit() && s.Active == 2, "drain start")
		s.Finish()
		s.Finish()
		check(!s.Accepting && s.Active == 0, "stopped")
	}

	// Retain unfinished work evidence
	{
		s := ServiceState{Accepting: true, Active: 1}
		check(s.Admit() && s.Active == 2, "admitted")
		s.Drain()
		budget := 1
		for i := 0; i < budget; i++ {
			s.Finish()
		}
		check(s.Active == 1, "unfinished work")
	}

	// Transfer deterministic version metadata
	{
		label := fmt.Sprintf("%s/%s revision=%s", "lesson", "1.0", "abc123")
		check(label == "lesson/1.0 revision=abc123", "version")
	}
	fmt.Println("All lesson checks passed.")
}
