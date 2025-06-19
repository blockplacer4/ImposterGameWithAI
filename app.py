import os
import random

from openai import OpenAI
from dotenv import load_dotenv
from pydantic import Secret

from utils.crewmate import Crewmate
from utils.imposter import Imposter

load_dotenv()

def load_sysprompt():
    try:
        with open("sysprompt.txt", "r", encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError("System prompt file 'sysprompt.txt' not found. Please create it with the required content.")

def init_ai_client():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please set the OPENROUTER_API_KEY environment variable.")

    return OpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key=api_key,
    )

def main():
    print("Welcome to the AI Game!")
    secret_word = input("Please enter the secret word as the game master: ").strip()
    try:
        sysprompt = load_sysprompt()
        ai_client = init_ai_client()
        print("AI client initialized successfully.")
    except Exception as e:
        print(f"Error initializing AI client or loading system prompt: {e}")
        return

    print("Creating players...")
    players = [
        Crewmate(name="Crewmate1", ai_client=ai_client, sysprompt=sysprompt, secret_word=secret_word),
        Crewmate(name="Crewmate2", ai_client=ai_client, sysprompt=sysprompt, secret_word=secret_word),
        Imposter(name="Imposter1", ai_client=ai_client, sysprompt=sysprompt)
    ]

    random.shuffle(players)

    print("Players created and shuffled.")
    print("Initializing players on the API...")
    all_initialized = True
    for player in players:
        try:
            response = player.initialize_on_api()
            print(f"{player.role} {player.name} initialized successfully with response: {response}")
        except Exception as e:
            print(f"Error initializing player {player.name}: {e}")
    print("All players initialized.")

    print("Game setup complete. Players are ready to take turns.")
    print("First round of turns begins...")

    game_history = []

    for player in players:
        print(f"{player.role} {player.name} is taking their turn...")
        try:
            turn_data = player.take_turn(game_history)
            word_said = turn_data.get("word_said", "")
            response = turn_data.get("response", "")

            print(f"{player.role} {player.name} said the word: {word_said}")
            print(f"Response from {player.role} {player.name}: {response}")

            game_history.append({"player": player.name, "word": word_said, "response": response})
        except Exception as e:
            print(f"Error during {player.role} {player.name}'s turn: {e}")

    print("Game round complete. Game history:")
    for entry in game_history:
        print(f"{entry['player']} said '{entry['word']}' with response: {entry['response']}")


if __name__ == "__main__":
    main()