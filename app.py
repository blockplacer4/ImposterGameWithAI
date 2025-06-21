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

def comment_on_last_turn(player, game_history):
    if not game_history:
        return "No previous turns to comment on."

    comment_data = player.comment_on_turn(game_history)
    if not comment_data:
        return "No comment data returned."
    action = comment_data.get("action", "")
    commented_word = comment_data.get("comment_on_word", "Unknown")
    commented_text = comment_data.get("comment_text", "")
    thought_process = comment_data.get("thought_process", "") # no need rn
    response_process = comment_data.get("response_process", "") # this is doubled up, but kept for compatibility

    if action != "make_comment":
        return f"Unexpected action '{action}' for {player.role} {player.name}."
    if commented_text == "NO_COMMENT" or not commented_text:
        return f"{player.role} {player.name} has no comment on the last turn."

    game_history.append({"player": player.name, "action": "make_comment", "word": commented_word, "response": commented_text})

    return f"{player.role} {player.name} commented on the last turn: '{commented_text}' about the word '{commented_word}'"

def take_turns(players, rounds, winning_word=None):
    game_history = []
    for i in range(rounds):
        print(f"\nRound {i + 1} starts now!")
        for player in players:
            print(f"{player.role} {player.name} is taking their turn...")
            try:
                turn_data = player.take_turn(game_history)
                # print(f"Turn data for {player.role} {player.name}: {turn_data}")
                word_said = turn_data.get("word_said", "")
                response = turn_data.get("response_text", "")
                thought_process = turn_data.get("thought_process", "")

                print(f"{player.role} {player.name} said the word: {word_said}")
                print(f"Response from {player.role} {player.name}: {response}")
                # print(f"Thought process of {player.role} {player.name}: {thought_process}")
                print()

                if player.role == "Imposter" and word_said.lower() == winning_word.lower():
                    raise ValueError(f"Imposter {player.name} said the secret word! This is a win for the imposter.")

                game_history.append({"player": player.name, "action": "say_word", "word": word_said, "response": response})
                random_player = random.choice([p for p in players if p != player])
                if random_player != player:
                    comment = comment_on_last_turn(random_player, game_history)
                    print(f"{random_player.role} {random_player.name} commented: {comment}")
            except Exception as e:
                print(f"Error during {player.role} {player.name}'s turn: {e}")

        print("Game round complete. Game history:")
        for entry in game_history:
            # print(f"{entry['player']} said '{entry['word']}' with response: {entry['response']} and thought process: {entry.get('thought_process', '')}")
            print(f"{entry['player']} said '{entry['word']}' with response: {entry['response']}")
    return game_history

def vote_imposter(players, game_history):
    for player in players:
        try:
            vote_data = player.take_vote(game_history)
            if vote_data.get("action") != "cast_vote":
                raise ValueError(f"Vote action for {player.role} {player.name} is not 'cast_vote'.")

            vote_for = vote_data.get("vote_for", "")
            # justification = vote_data.get("justification", "")
            response_text = vote_data.get("response_text", "")
            print(f"{player.role} {player.name} votes for {vote_for} with response: {response_text}")
        except Exception as e:
            print(f"Error during voting for {player.role} {player.name}: {e}")

def main(rounds: int = 1):
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

    for player in players:
        try:
            response = player.initialize_on_api()
            print(f"{player.role} {player.name} initialized successfully with response: {response}")
        except Exception as e:
            print(f"Error initializing player {player.name}: {e}")

    print("All players initialized.")
    print("Game setup complete. Players are ready to take turns.")

    game_history = take_turns(players, rounds, winning_word=secret_word)

    print("Voting phase begins...")
    vote_imposter(players, game_history)

    print("Game over. Thank you for playing!")


if __name__ == "__main__":
    main(rounds=3)