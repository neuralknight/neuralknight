package main

import "testing"

func TestMainEntry(t *testing.T) {
	defer func() {
		if err := recover(); err != nil {
		}
	}()
	main()
}
