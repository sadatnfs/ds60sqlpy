package main

import (
	"fmt"
	"sync/atomic"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type Published struct {
	Count int
	Ready bool
}

func main() {
	// Publish through a channel
	{
		ch := make(chan Published)
		go func() { ch <- Published{Count: 3, Ready: true} }()
		v := <-ch
		check(v.Ready && v.Count == 3, "publication")
	}

	// Publish through closure
	{
		done := make(chan struct{})
		n := 0
		go func() { n = 7; close(done) }()
		<-done
		check(n == 7, "close publication")
	}

	// Publish an atomic value
	{
		var current atomic.Value
		current.Store(Published{Count: 4, Ready: true})
		v := current.Load().(Published)
		check(v.Count == 4 && v.Ready, "atomic value")
	}

	// Retain a previous snapshot
	{
		var current atomic.Value
		current.Store(Published{Count: 4})
		old := current.Load().(Published)
		current.Store(Published{Count: 5})
		check(old.Count == 4 && current.Load().(Published).Count == 5, "replacement")
	}

	// Copy reference-containing data
	{
		original := []int{1, 2}
		snapshot := append([]int(nil), original...)
		original[0] = 9
		check(snapshot[0] == 1, "independent data")
	}

	// Transfer local construction
	{
		ch := make(chan string)
		go func() { ch <- fmt.Sprintf("ready:%d", 3) }()
		check(<-ch == "ready:3", "result")
	}
	fmt.Println("All lesson checks passed.")
}
