package math

type Number interface {
	~int | ~int64
}

type (
	Operation string
	Calculator struct{}
)

func Add[T Number](left, right T) T {
	return left + right
}

func (Calculator) Sum(values ...int) int {
	total := 0
	for _, value := range values {
		total += value
	}
	return total
}
