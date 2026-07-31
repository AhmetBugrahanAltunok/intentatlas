package main

import (
	"example.com/intentatlas/fixture/internal/math"
	"example.com/intentatlas/plugin/worker"
)

func main() {
	_ = math.Add(1, 2)
	worker.Run()
}
