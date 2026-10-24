package main

import (
	"fmt"
	"sync"
	"sync/atomic"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type LockedCount struct {
	mu sync.Mutex
	n  int
}

func (c *LockedCount) Inc()       { c.mu.Lock(); defer c.mu.Unlock(); c.n++ }
func (c *LockedCount) Value() int { c.mu.Lock(); defer c.mu.Unlock(); return c.n }

type Pair struct {
	mu   sync.Mutex
	A, B int
}

func (p *Pair) Transfer(n int)       { p.mu.Lock(); defer p.mu.Unlock(); p.A -= n; p.B += n }
func (p *Pair) Snapshot() (int, int) { p.mu.Lock(); defer p.mu.Unlock(); return p.A, p.B }

func main() {
	// Protect a concurrent count
	{
		c := &LockedCount{}
		var wg sync.WaitGroup
		for i := 0; i < 4; i++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for j := 0; j < 100; j++ {
					c.Inc()
				}
			}()
		}
		wg.Wait()
		check(c.Value() == 400, "count")
	}

	// Use a typed atomic
	{
		var n atomic.Int64
		n.Add(3)
		n.Add(4)
		check(n.Load() == 7, "atomic")
	}

	// Protect a pair relationship
	{
		p := &Pair{A: 5, B: 5}
		p.Transfer(3)
		a, b := p.Snapshot()
		check(a == 2 && b == 8 && a+b == 10, "pair")
	}

	// Initialize once
	{
		var once sync.Once
		n := 0
		for i := 0; i < 3; i++ {
			once.Do(func() { n++ })
		}
		check(n == 1, "once")
	}

	// Reject a stale atomic expectation
	{
		var n atomic.Int64
		n.Store(2)
		check(n.CompareAndSwap(2, 3), "CAS")
		check(!n.CompareAndSwap(2, 4) && n.Load() == 3, "stale")
	}

	// Transfer safe observation
	{
		p := &Pair{A: 4, B: 6}
		a, b := p.Snapshot()
		c, d := p.Snapshot()
		check(a+b == 10 && c+d == 10, "snapshot")
	}
	fmt.Println("All lesson checks passed.")
}
