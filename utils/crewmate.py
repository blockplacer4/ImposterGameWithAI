from utils.player import Player
from openai import OpenAI

class Crewmate(Player):
    def __init__(self, name: str, ai_client: OpenAI, sysprompt: str, secret_word: str):
        super().__init__(name, ai_client, sysprompt, secret_word)
        self.role = "Crewmate"