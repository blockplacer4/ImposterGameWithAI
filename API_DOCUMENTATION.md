# Imposter Game - API Documentation

This document provides the technical details for integrating a client application with the Imposter Game backend.

## Base URL

The server runs on `http://127.0.0.1:8080` by default.

---

## 1. REST API

The REST API is used for setting up the game lobby.

### Create Game Lobby

Creates a new game session and returns a unique ID for it.

- **Endpoint:** `/lobby`
- **Method:** `POST`
- **Request Body:** `application/json`

#### Request Payload

| Field           | Type      | Required? | Description                                                              |
| --------------- | --------- | --------- | ------------------------------------------------------------------------ |
| `language`      | `string`  | No        | Language for the AI (e.g., "en", "de"). Defaults to "en".                |
| `player_name`   | `string`  | Yes       | The name of the human player.                                            |
| `player_role`   | `string`  | Yes       | The desired role: `"crewmate"` or `"imposter"`.                          |
| `num_agents`    | `integer` | Yes       | Number of AI players to compete against (valid range: 1-5).              |
| `difficulty`    | `string`  | Yes       | AI difficulty: `"easy"`, `"medium"`, or `"hard"`.                        |
| `secret_word`   | `string`  | If Crewmate | The secret word. Required only if `player_role` is `"crewmate"`.         |

**Example Request:**
```json
{
  "language": "en",
  "player_name": "MobileUser",
  "player_role": "crewmate",
  "num_agents": 3,
  "difficulty": "medium",
  "secret_word": "Spaceship"
}
```

#### Response Payload (Success)

- **Status Code:** `200 OK`
- **Body:** `application/json`

**Example Response:**
```json
{
  "lobby_id": "lobby_f9469b3e834a3f9e"
}
```
This `lobby_id` is required to connect to the WebSocket.

---

## 2. WebSocket API

The WebSocket is used for real-time gameplay after a lobby has been created.

### Connection URL

- **Format:** `ws://127.0.0.1:8080/ws/{lobby_id}/{user_name}`
- **Parameters:**
  - `{lobby_id}`: The ID returned from the `/lobby` endpoint.
  - `{user_name}`: The name of the connecting player.

### Message Format

All communication over the WebSocket is done via JSON-formatted strings.

### Client-to-Server Messages (Commands)

Your application sends these messages to control the game flow.

1.  **Start the Game**
    - **Purpose:** To begin the game after all players have connected. This must be sent once after connecting.
    - **Payload:**
      ```json
      { "command": "start_game" }
      ```

2.  **Submit a Word**
    - **Purpose:** To submit the human player's word when it's their turn.
    - **Payload:**
      ```json
      { "command": "submit_word", "word": "YourChosenWord" }
      ```

### Server-to-Client Messages (Events)

Your application must listen for these events to update the UI and manage the game state.

1.  **`user_joined`**
    - **Purpose:** Informs that a user has connected. Provides the full list of players.
    - **Payload:**
      ```json
      {
        "event": "user_joined",
        "user_name": "MobileUser",
        "players": [
          { "name": "Agent1", "role": "Crewmate" },
          { "name": "MobileUser", "role": "Crewmate" },
          { "name": "Agent2", "role": "Imposter" }
        ]
      }
      ```

2.  **`initializing_players`**
    - **Purpose:** Indicates that the server is initializing the AI agents. You can show a loading indicator in the UI.
    - **Payload:** `{"event": "initializing_players"}`

3.  **`game_started`**
    - **Purpose:** The game has officially begun.
    - **Payload:** `{"event": "game_started"}`

4.  **`ai_thinking`**
    - **Purpose:** Signals that an AI player is currently generating its response. Useful for showing a "thinking..." status in the UI.
    - **Payload:** `{"event": "ai_thinking"}`

5.  **`turn_result`**
    - **Purpose:** Provides the result of a completed turn (from either a human or an AI).
    - **Payload:**
      ```json
      {
        "event": "turn_result",
        "data": {
          "player_name": "Agent1",
          "player_role": "Crewmate",
          "turn_data": {
            "action": "say_word",
            "word_said": "Engine",
            "response_text": "My word is **Engine**."
          }
        }
      }
      ```

6.  **`human_turn_prompt`**
    - **Purpose:** Notifies the client that it is the human player's turn to act. The UI should now be enabled for input.
    - **Payload:**
      ```json
      {
        "event": "human_turn_prompt",
        "player_name": "MobileUser"
      }
      ```

7.  **`user_left`**
    - **Purpose:** Informs that a user has disconnected.
    - **Payload:** `{"event": "user_left", "user_name": "MobileUser"}`

---

## 3. Application Flow Example

1.  App sends `POST /lobby` request.
2.  App receives `{ "lobby_id": "..." }`.
3.  App opens WebSocket connection to `ws://.../{lobby_id}/{player_name}`.
4.  App sends `{"command": "start_game"}`.
5.  App listens for events:
    - On `turn_result`, update the game history in the UI.
    - On `human_turn_prompt`, enable the text input field for the user.
    - When the user submits their word, the app sends `{"command": "submit_word", "word": "..."}`.
    - On `ai_thinking`, show a loading/thinking indicator.
6.  This cycle continues until the game ends.
