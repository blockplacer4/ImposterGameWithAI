from utils.player import Player
from openai import OpenAI

class Crewmate(Player):
    def __init__(self, name: str, ai_client: OpenAI, sysprompt: str, secret_word: str, language: str = "en"):
        super().__init__(name, ai_client, sysprompt, secret_word, language)
        self.role = "Crewmate"