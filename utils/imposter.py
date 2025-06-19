from utils.player import Player
from openai import OpenAI

class Imposter(Player):
    def __init__(self, name: str, ai_client: OpenAI, sysprompt: str):
        super().__init__(name, ai_client, sysprompt, "UNKNOWN")
        self.role = "Imposter"



