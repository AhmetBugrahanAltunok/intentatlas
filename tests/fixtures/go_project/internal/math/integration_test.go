package math_test

import (
	fixturemath "example.com/intentatlas/fixture/internal/math"
	"testing"
)

func TestIntegration(t *testing.T) {
	if fixturemath.Add(2, 3) != 5 {
		t.Fatal("unexpected sum")
	}
}
