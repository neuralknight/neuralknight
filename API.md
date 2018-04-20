# API Endpoints

All parameters are expected to be JSON unless otherwise specified.

## /issue-agent

### POST

#### Returns id of an agent that is able to interact with a specified game.

Expected parameter:
  "id" - The id of a game the agent is to join.
Optional parameter:
  "user" - If this parameter is passed (with any value), a user agent, as opposed to an AI agent, is returned.
Response:
  {'agent_id': *agent_id*}

## /issue-agent-lookahead

### POST

#### Returns an agent that looks ahead a specified number of game states

Expected parameters:
  "id" - The id of a game the agent is to join.
  "lookahead" - The number of game states - ply - the agent should try to forecast
Response:
  {'agent_id': *agent_id*}

## /agent

### PUT

#### Instructs a chosen agent to return a new board state - i.e. take a turn

Expected parameters:
  "id" - The id of the agent that should a new board state

## /v1.0/games

### GET

#### Returns all existing game id's

Expected parameters:
  None
Response:
  {'ids': *(game_id_1, game_id_2,...)*}

### POST

#### Returns id of a newly instantiated game

Expected parameters:
  None
Response:
  {'id': *game_id*}

## /v1.0/games/{game}/states
*game* query string is a game_id

### GET

#### Returns a series of possible next board states

Expected parameters:
  None
Optional parameters:
  "cursor" - The cursor that indicates we would like the next set of board state possibilities
Response:
  {'boards': *series of board states*, 'cursor': *cursor for the next slice of states*}

## /v1.0/games/{game}
*game* query string is a game_id

### GET

#### Returns current board state

Expected parameters:
  None
Response:
  {'state': *board_state*}

### POST

#### Adds an agent to board

Expected parameters:
  "id" - Agent id to be added to the board

### PUT

#### Updates current board state

Expected parameters:
  "state" - Chosen new board state

## /v1.0/games/{game}/info
*game* query string is a game_id

### GET

#### Provides a printable version of the current board state

Response:
  {'print': *board_state string*}
