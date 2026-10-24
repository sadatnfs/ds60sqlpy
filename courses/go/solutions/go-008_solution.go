package main

import (
	"errors"
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type Point struct{ X, Y int }
type Batch struct{ Items []int }
type Item struct{ Name string }

func newItem(name string) (Item, error) {
	if name == "" {
		return Item{}, errors.New("name required")
	}
	return Item{Name: name}, nil
}

func main() {
	// Model a coordinate
	{
		p := Point{X: 2, Y: 3}
		check(p.X+p.Y == 5, "point")
	}

	// Observe scalar copy
	{
		a := Point{X: 2, Y: 3}
		b := a
		b.X = 9
		check(a.X == 2 && b.X == 9, "struct copy")
	}

	// Expose a shallow field
	{
		a := Batch{Items: []int{1, 2}}
		b := a
		b.Items[0] = 9
		check(a.Items[0] == 9, "shallow field")
	}

	// Inspect zero state
	{
		var p Point
		check(p == (Point{X: 0, Y: 0}), "struct zero")
	}

	// Use a comparable key
	{
		m := map[Point]string{{X: 0, Y: 0}: "origin"}
		check(m[Point{}] == "origin", "struct key")
	}

	// Transfer validation
	{
		_, err := newItem("")
		check(err != nil, "blank name")
		item, err := newItem("sample")
		check(err == nil && item.Name == "sample", "valid item")
	}
	fmt.Println("All lesson checks passed.")
}
