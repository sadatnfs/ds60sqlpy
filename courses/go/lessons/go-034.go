package main

import "fmt"

func main() {
	// Exercise 1: Inspect the current target: predict an edited check: Copy worked example 1, change `check(runtime.GOOS != "" && runtime.GOARCH != "", "target")` to `check(runtime.GOOS == "" && runtime.GOARCH != "", "target")` inside its check and predict whether it still passes; then restore it.
	// Expected: The edited check panics with `target` even though `runtime.GOOS != "" && runtime.GOARCH != ""` still holds.

	// Exercise 2: Validate the running deployment tuple: debug a regression: A one-token regression in worked example 2 makes a line read `allowed := map[string]bool{"linux/amd64": true, "linux/arm65": true}`. Repair it without changing the check.
	// Expected: The defective run panics with `running target`; after restoring `allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}`, the running Linux tuple is admitted.

	// Exercise 3: Refuse an unsupported tuple: Check plan9/386 and an incomplete linux tuple with the same lookup, keeping linux/arm64 as the control.
	// Expected: Both unsupported tuples are rejected while linux/arm64 is admitted.

	// Exercise 4: Model stop-accepting before drain: Start with two active tasks, drain the service, try to admit a third task, then finish both tasks.
	// Expected: The third task is refused once draining begins, and the service stops only after both tasks finish.

	// Exercise 5: Retain unfinished work evidence: Admit one more task to a service already running one, drain it, and allow a shutdown budget of one completion.
	// Expected: One of the two tasks remains unfinished and visible.

	// Exercise 6: Transfer deterministic version metadata: Format a version and source revision into a build label.
	// Expected: The result is lesson/1.0 revision=abc123.

	fmt.Println("Implement the six investigations in your saved pad.")
}
