from utils.player import Player
from openai import OpenAI

class Crewmate(Player):
    def __init__(self, name: str, ai_client: OpenAI, sysprompt: str, secret_word: str):
        super().__init__(name, ai_client, sysprompt)
        self.role = "Crewmate"
        self.secret_word = secret_word

    def initialize_on_api(self):
        init_json = {
            "type": "init",
            "role": self.role,
            "secret_word": self.secret_word
        }
        response_data = self._call_ai(init_json)

        if response_data.get("type") != "init_response":
            raise ValueError("Initialization response type is not 'init_response'.")
        if response_data.get("role") != self.role:
            raise ValueError(f"Expected role '{self.role}', but got '{response_data.get('role')}'.")
        if response_data.get("secret_word") != self.secret_word:
            raise ValueError(f"Expected secret word '{self.secret_word}', but got '{response_data.get('secret_word')}'.")

        print(f"Initialization response: {response_data}")
        return response_data