package views_test

import (
	_ "github.com/jinzhu/gorm/dialects/sqlite"
	. "gopkg.in/check.v1"
)

type GamesSuite struct{}

var _ = Suite(&GamesSuite{})

func (s *GamesSuite) TestBoardView(c *C) {

}
