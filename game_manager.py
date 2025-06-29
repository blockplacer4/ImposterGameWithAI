import os
import random
import secrets
import logging
import asyncio
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv

from models import CreateLobbyRequest, PlayerRole
from utils.crewmate import Crewmate
from utils.imposter import Imposter
from utils.player import Player
from words import get_random_word

load_dotenv()

def load_sysprompt():
    try:
        with open("sysprompt.txt", "r", encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError("System prompt file 'sysprompt.txt' not found.")

def init_ai_client():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please set OPENROUTER_API_KEY.")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

class GameManager:
    def __init__(self):
        self.lobbies: Dict[str, Dict] = {}
        self.ai_client = init_ai_client()
        self.sysprompt = load_sysprompt()
        logging.info("GameManager initialized.")

    def create_lobby(self, request: CreateLobbyRequest) -> (str, str):
        lobby_id = f"lobby_{secrets.token_hex(8)}"
        logging.info(f"Creating lobby '{lobby_id}' for human player '{request.player_name}'.")
        
        secret_word = get_random_word(request.difficulty)
        
        players: List[Player] = []
        
        if request.player_role == PlayerRole.IMPOSTER:
            human_player = Imposter(name=request.player_name, ai_client=self.ai_client, sysprompt=self.sysprompt, language=request.language)
        else:
            human_player = Crewmate(name=request.player_name, ai_client=self.ai_client, sysprompt=self.sysprompt, secret_word=secret_word, language=request.language)
        players.append(human_player)

        agent_names = ["Agent1", "Agent2", "Agent3", "Agent4", "Agent5"]
        random.shuffle(agent_names)
        
        num_imposters = 1 if request.difficulty in ["easy", "medium"] else 2
        if request.player_role == PlayerRole.IMPOSTER:
            num_imposters -= 1

        for i in range(request.num_agents):
            agent_name = agent_names[i]
            if i < num_imposters:
                agent = Imposter(name=agent_name, ai_client=self.ai_client, sysprompt=self.sysprompt, language=request.language)
            else:
                agent = Crewmate(name=agent_name, ai_client=self.ai_client, sysprompt=self.sysprompt, secret_word=secret_word, language=request.language)
            players.append(agent)
            
        random.shuffle(players)

        self.lobbies[lobby_id] = {
            "settings": request.dict(),
            "human_player_name": request.player_name,
            "players": players,
            "game_history": [],
            "current_player_index": 0,
            "game_state": "pending_initialization"
        }
        
        return lobby_id, secret_word

    async def initialize_players_async(self, lobby_id: str):
        lobby = self.get_lobby(lobby_id)
        if not lobby: return
        logging.info(f"Initializing players for lobby '{lobby_id}'...")
        tasks = [p.initialize_on_api() for p in lobby["players"]]
        await asyncio.gather(*tasks)
        lobby["game_state"] = "ready"
        logging.info(f"All players for lobby '{lobby_id}' initialized.")

    def get_lobby(self, lobby_id: str):
        return self.lobbies.get(lobby_id)

    def _advance_turn(self, lobby: dict):
        lobby["current_player_index"] = (lobby["current_player_index"] + 1) % len(lobby["players"])

    async def ai_take_turn(self, lobby_id: str):
        lobby = self.get_lobby(lobby_id)
        if not lobby or lobby["game_state"] != "running": return None
        player = lobby["players"][lobby["current_player_index"]]
        
        turn_data = await player.take_turn(lobby["game_history"])
        lobby["game_history"].append({"player": player.name, "action": "say_word", "word": turn_data.get("word_said"), "response": turn_data.get("response_text")})
        self._advance_turn(lobby)
        return {"player_name": player.name, "player_role": player.role, "turn_data": turn_data}

    def human_take_turn(self, lobby_id: str, word: str):
        lobby = self.get_lobby(lobby_id)
        if not lobby or lobby["game_state"] != "running": return None
        player = lobby["players"][lobby["current_player_index"]]

        turn_data = {"action": "say_word", "word_said": word, "response_text": f"I have chosen the word: **{word}**"}
        lobby["game_history"].append({"player": player.name, "action": "say_word", "word": word, "response": turn_data["response_text"]})
        self._advance_turn(lobby)
        return {"player_name": player.name, "player_role": player.role, "turn_data": turn_data}