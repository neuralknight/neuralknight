package neuralknightviews

import (
	"net/http"
	"regexp"

	"github.com/neuralknight/neuralknight/models"
	"github.com/satori/go.uuid"
)

var routerV1Games = regexp.MustCompile("^api/v1.0/games/?$")
var routerV1GamesID = regexp.MustCompile("^api/v1.0/games/[\\w-]+/?$")
var extractV1GamesID = regexp.MustCompile("(?:/)[\\w-]+(?:/?)$")

// ServeAPIGamesHTTP neuralknightviews.
func ServeAPIGamesHTTP(w http.ResponseWriter, r *http.Request) {
	if routerV1Games.MatchString(r.URL.Path) {
		serveAPIGamesListHTTP(w, r)
		return
	}
	if routerV1GamesID.MatchString(r.URL.Path) {
		serveAPIGamesIDHTTP(w, r)
		return
	}
	http.NotFound(w, r)
}

func serveAPIGamesListHTTP(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodPost:
		neuralknightmodels.MakeAgent(w, r)
		return
	}
	http.NotFound(w, r)
}

func serveAPIGamesIDHTTP(w http.ResponseWriter, r *http.Request) {
	gameID, err := uuid.FromString(extractV1GamesID.FindString(r.URL.Path))
	if err != nil {
		panic(err)
	}
	game := neuralknightmodels.AgentPool[gameID]
	switch r.Method {
	case http.MethodGet:
		game.GetState(w, r)
		return
	case http.MethodPut:
		game.PlayRound(w, r)
		return
	}
	http.NotFound(w, r)
}

// from cornice import Service
// from operator import methodcaller
// from pyramid.httpexceptions import HTTPBadRequest
//
// from ..models.board import Board, NoBoard
// from ..models.board_model import InvalidMove
//
// games = Service(
//     name="games",
//     path="/v1.0/games",
//     description="Create game")
// game_states = Service(
//     name="game_states",
//     path="/v1.0/games/{game}/states",
//     description="Game states")
// game_interaction = Service(
//     name="game_interaction",
//     path="/v1.0/games/{game}",
//     description="Game interaction")
// game_info = Service(
//     name="game_info",
//     path="/v1.0/games/{game}/info",
//     description="Game info")
//
//
// class BlankBoard:
//     def __str__(self):
//         return "\n" * 8
//
//     def add_player_v1(self, *args, **kwargs):
//         return {}
//
//     def close(self, *args, **kwargs):
//         return {"end": True}
//
//     def current_state_v1(self, *args, **kwargs):
//         return {"state": {"end": True}}
//
//     def slice_cursor_v1(self, *args, **kwargs):
//         return {"cursor": None, "boards": []}
//
//     def update_state_v1(self, *args, **kwargs):
//         return {"end": True}
//
//
// def get_game(request):
//     """
//     Retrieve board for request.
//     """
//     try:
//         return Board.get_game(request.matchdict["game"])
//     except NoBoard:
//         pass
//     return BlankBoard()
//
//
// @games.get()
// def get_games(request):
//     """
//     Retrieve all game ids.
//     """
//     return {"ids": tuple(Board.GAMES.keys())}
//
//
// @games.post()
// def post_game(request):
//     """
//     Create a new game and provide an id for interacting.
//     """
//     return {"id": Board().id}
//
//
// @game_states.get()
// def get_states(request):
//     """
//     Start or continue a cursor of next board states.
//     """
//     cursor = get_game(request).slice_cursor_v1(**request.GET)
//     cursor["boards"] = tuple(map(
//         lambda boards: tuple(map(
//             lambda board: tuple(map(methodcaller("hex"), board)),
//             boards)),
//         cursor["boards"]))
//     return cursor
//
//
// @game_interaction.get()
// def get_state(request):
//     """
//     Provide current state on the board.
//     """
//     state = get_game(request).current_state_v1()
//     if isinstance(state["state"], dict):
//         return state
//     state["state"] = tuple(map(methodcaller("hex"), state["state"]))
//     return state
//
//
// @game_interaction.post()
// def join_game(request):
//     """
//     Add player to board.
//     """
//     try:
//         user_id = request.json["id"]
//     except KeyError:
//         raise HTTPBadRequest
//     return get_game(request).add_player_v1(request.dbsession, user_id)
//
//
// @game_interaction.put()
// def put_state(request):
//     """
//     Make a move to a new state on the board.
//     """
//     try:
//         return get_game(request).update_state_v1(request.dbsession, **request.json)
//     except InvalidMove:
//         pass
//     return {"invalid": True}
//
//
// @game_info.get()
// def get_info(request):
//     """
//     Provide current state on the board.
//     """
//     return {"print": str(get_game(request))}
