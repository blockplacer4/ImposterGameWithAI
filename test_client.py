import asyncio
import websockets
import requests
import json
import logging
from typing import List, Dict

# --- Helper Functions for UI ---
def print_header(text: str):
    print("\n" + "="*50)
    print(f" {text.upper()} ".center(50, "="))
    print("="*50)

def print_players(players: List[Dict]):
    print("\n--- PLAYERS IN LOBBY ---")
    for player in players:
        print(f"- {player['name']} (Role: {player['role']})")
    print("------------------------\n")

async def run_test_client():
    print_header("Imposter Game Test Client")
    player_name = input("Enter your name: ").strip()
    
    role_choice = ""
    while role_choice not in ["1", "2"]:
        role_choice = input("Choose your role (1: Crewmate, 2: Imposter): ").strip()
    player_role = "crewmate" if role_choice == "1" else "imposter"

    secret_word = ""
    if player_role == "crewmate":
        secret_word = input("Enter the secret word for the crewmates: ").strip()

    language = input("Enter game language (e.g., 'en', 'de') [default: en]: ").strip() or "en"
    
    num_agents = 0
    while not 1 <= num_agents <= 5:
        try:
            num_agents = int(input("Enter number of AI agents (1-5): ").strip())
        except ValueError:
            print("Please enter a valid number.")

    difficulty_choice = ""
    while difficulty_choice not in ["1", "2", "3"]:
        difficulty_choice = input("Choose difficulty (1: Easy, 2: Medium, 3: Hard): ").strip()
    difficulty_map = {"1": "easy", "2": "medium", "3": "hard"}
    difficulty = difficulty_map[difficulty_choice]

    print_header("Creating Lobby")
    lobby_payload = {
        "language": language, "player_name": player_name, "player_role": player_role,
        "num_agents": num_agents, "difficulty": difficulty, "secret_word": secret_word,
    }
    url = "http://127.0.0.1:8080/lobby"
    
    try:
        response = requests.post(url, json=lobby_payload, timeout=15)
        response.raise_for_status()
        lobby_id = response.json()["lobby_id"]
        print(f"Lobby created successfully! Lobby ID: {lobby_id}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating lobby: {e.response.text if e.response else e}")
        return

    uri = f"ws://127.0.0.1:8080/ws/{lobby_id}/{player_name}"
    print(f"\nConnecting to WebSocket at {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            await websocket.send(json.dumps({"command": "start_game"}))

            while True:
                message = json.loads(await websocket.recv())
                event = message.get("event")

                if event == "user_joined":
                    print_header(f"User '{message.get('user_name')}' Joined")
                    print_players(message.get("players", []))

                elif event == "initializing_players":
                    print_header("AI Players are getting ready...")

                elif event == "game_started":
                    print_header("Game Started!")

                elif event == "ai_thinking":
                    print("\n... AI is thinking ...")

                elif event == "turn_result":
                    data = message.get("data", {})
                    p_name, p_role = data.get('player_name'), data.get('player_role')
                    turn_data = data.get('turn_data', {})
                    word, response_text = turn_data.get('word_said'), turn_data.get('response_text')
                    print_header(f"Turn: {p_name} ({p_role})")
                    print(f"Said: '{word}'")
                    print(f"Response: {response_text}")

                elif event == "human_turn_prompt":
                    next_player = message.get('player_name')
                    print_header(f"Your Turn, {next_player}!")
                    word_to_say = input("Enter the word you want to say: ").strip()
                    await websocket.send(json.dumps({"command": "submit_word", "word": word_to_say}))
                    print("... Word sent to server...")

    except websockets.exceptions.ConnectionClosed as e:
        print_header("Connection Lost")
        print(f"Reason: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    try:
        asyncio.run(run_test_client())
    except KeyboardInterrupt:
        print("\nClient stopped by user.")