//go:build intentatlas_fixture

package main

import "example.net/external"

func externalFixture() string {
	return external.Name
}
