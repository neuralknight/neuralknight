package main

import "testing"

func TestMain(t *testing.T) {
	defer func() {
		if err := recover(); err != nil {
		}
	}()
	main()
}
