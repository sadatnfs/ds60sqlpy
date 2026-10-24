package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func produce(out chan<- int) { defer close(out); out <- 1; out <- 2 }

func main() {
	// Drain before iteration ends
	{
		ch := make(chan int, 2)
		ch <- 2
		ch <- 3
		close(ch)
		sum := 0
		for v := range ch {
			sum += v
		}
		check(sum == 5, "drain")
	}

	// Distinguish zero from closed
	{
		ch := make(chan int, 1)
		ch <- 0
		close(ch)
		a, okA := <-ch
		b, okB := <-ch
		check(a == 0 && b == 0 && okA && !okB, "closed presence")
	}

	// Use sender ownership
	{
		ch := make(chan int)
		go produce(ch)
		count := 0
		for range ch {
			count++
		}
		check(count == 2, "producer close")
	}

	// Inspect bounded buffering
	{
		ch := make(chan int, 2)
		ch <- 4
		ch <- 5
		check(len(ch) == 2 && cap(ch) == 2, "buffer")
		<-ch
		<-ch
	}

	// Disable a nil select arm
	{
		var disabled <-chan int
		ready := make(chan struct{})
		close(ready)
		selected := false
		select {
		case <-disabled:
			panic("nil selected")
		case <-ready:
			selected = true
		}
		check(selected, "nil arm")
	}

	// Transfer independent message storage
	{
		original := []int{1}
		ch := make(chan []int, 1)
		ch <- append([]int(nil), original...)
		original[0] = 9
		received := <-ch
		check(received[0] == 1, "copy")
	}
	fmt.Println("All lesson checks passed.")
}
