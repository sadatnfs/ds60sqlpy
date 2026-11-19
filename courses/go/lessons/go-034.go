package main

import "fmt"

func main() {
	// Exercise 1: Inspect the current target: predict an edited check: Copy worked example 1 into a scratch pad and change `check(runtime.GOOS != "" && runtime.GOARCH != "", "target")` to `check(runtime.GOOS == "" && runtime.GOARCH != "", "target")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `target` because the edited check no longer holds. Restoring the original line brings back the worked observation: both identifiers are nonempty.

	// Exercise 2: Validate the running deployment tuple: debug a regression: A regression changed one token in worked example 2, so one line now reads `allowed := map[string]bool{"linux/amd64": true, "linux/arm65": true}`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `running target`; after it the line reads `allowed := map[string]bool{"linux/amd64": true, "linux/arm64": true}` again and the running Linux tuple is admitted.

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
