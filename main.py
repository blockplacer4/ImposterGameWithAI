import secrets
import json
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from models import CreateLobbyRequest
from game_manager import GameManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Application startup: Initializing GameManager...")
    app.state.game_manager = GameManager()
    yield
    logging.info("Application shutdown: Cleaning up resources.")

app = FastAPI(lifespan=lifespan)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, websocket: WebSocket, lobby_id: str, user_name: str):
        await websocket.accept()
        if lobby_id not in self.active_connections:
            self.active_connections[lobby_id] = []
        self.active_connections[lobby_id].append({"user_name": user_name, "ws": websocket})
        logging.info(f"User '{user_name}' connected to lobby '{lobby_id}'.")

    def disconnect(self, websocket: WebSocket, lobby_id: str):
        if lobby_id in self.active_connections:
            self.active_connections[lobby_id] = [c for c in self.active_connections[lobby_id] if c["ws"] != websocket]
            logging.info(f"WebSocket disconnected from lobby '{lobby_id}'.")

    async def broadcast(self, lobby_id: str, message: dict):
        if lobby_id in self.active_connections:
            # logging.info(f"Broadcasting to lobby '{lobby_id}': {message}")
            for connection in self.active_connections[lobby_id]:
                await connection["ws"].send_json(message)

connection_manager = ConnectionManager()

@app.post("/lobby")
async def create_lobby(request: CreateLobbyRequest, http_request: Request):
    game_manager = http_request.app.state.game_manager
    logging.info(f"Received request to create lobby from {http_request.client.host}")
    try:
        lobby_id, secret_word = game_manager.create_lobby(request)
        logging.info(f"Lobby '{lobby_id}' created successfully.")
        return {"lobby_id": lobby_id, "secret_word": secret_word}
    except Exception as e:
        logging.error(f"Error creating lobby: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def handle_turn(game_manager: GameManager, lobby_id: str):
    lobby = game_manager.get_lobby(lobby_id)
    if not lobby or lobby["game_state"] != "running":
        return

    player = lobby["players"][lobby["current_player_index"]]
    is_human = player.name == lobby["human_player_name"]

    if is_human:
        await connection_manager.broadcast(lobby_id, {"event": "human_turn_prompt", "player_name": player.name})
    else:
        asyncio.create_task(process_ai_turn(game_manager, lobby_id))

async def process_ai_turn(game_manager: GameManager, lobby_id: str):
    await connection_manager.broadcast(lobby_id, {"event": "ai_thinking"})
    turn_result = await game_manager.ai_take_turn(lobby_id)
    if turn_result:
        await connection_manager.broadcast(lobby_id, {"event": "turn_result", "data": turn_result})
        await asyncio.sleep(1)
        await handle_turn(game_manager, lobby_id)

@app.websocket("/ws/{lobby_id}/{user_name}")
async def websocket_endpoint(websocket: WebSocket, lobby_id: str, user_name: str):
    game_manager = websocket.app.state.game_manager
    lobby = game_manager.get_lobby(lobby_id)
    if not lobby:
        await websocket.close(code=1008)
        return
    
    await connection_manager.connect(websocket, lobby_id, user_name)
    player_list = [{"name": p.name, "role": p.role} for p in lobby["players"]]
    await connection_manager.broadcast(lobby_id, {"event": "user_joined", "user_name": user_name, "players": player_list})

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            command = message.get("command")

            if command == "start_game" and lobby["game_state"] == "pending_initialization":
                await connection_manager.broadcast(lobby_id, {"event": "initializing_players"})
                await game_manager.initialize_players_async(lobby_id)
                lobby["game_state"] = "running"
                await connection_manager.broadcast(lobby_id, {"event": "game_started"})
                await handle_turn(game_manager, lobby_id)

            elif command == "submit_word" and lobby["game_state"] == "running":
                word = message.get("word")
                turn_result = game_manager.human_take_turn(lobby_id, word)
                if turn_result:
                    await connection_manager.broadcast(lobby_id, {"event": "turn_result", "data": turn_result})
                    await asyncio.sleep(1)
                    await handle_turn(game_manager, lobby_id)

    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, lobby_id)
        await connection_manager.broadcast(lobby_id, {"event": "user_left", "user_name": user_name})
    except Exception as e:
        logging.error(f"Error in WebSocket for lobby '{lobby_id}': {e}", exc_info=True)
        connection_manager.disconnect(websocket, lobby_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8080, 
        ws_ping_interval=300, 
        ws_ping_timeout=300
    )