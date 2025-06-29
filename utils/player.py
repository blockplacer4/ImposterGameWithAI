from openai import OpenAI
import json
import asyncio

class Player:
    def __init__(self, name: str, ai_client: OpenAI, sysprompt: str, secret_word: str, language: str = "en"):
        if not name or not ai_client or not sysprompt:
            raise ValueError("Name, AI client, and system prompt must be provided.")
        self.name = name
        self.ai_client = ai_client
        self.sysprompt = sysprompt
        self.secret_word = secret_word
        self.conversation_history = [{"role": "system", "content": self.sysprompt}]
        self.role = "Not assigned"
        self.language = language

    async def _call_ai(self, user_message: dict) -> dict:
        self.conversation_history.append({"role": "user", "content": json.dumps(user_message)})
        try:
            # Wrap the synchronous, blocking call in asyncio.to_thread
            response = await asyncio.to_thread(
                self.ai_client.chat.completions.create,
                model="google/gemini-2.5-flash-lite-preview-06-17",
                messages=self.conversation_history,
                response_format={"type": "json_object"},
            )
            ai_message = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": ai_message})
            return json.loads(ai_message)
        except json.JSONDecodeError as e:
            print(f"AI response for {self.name} could not be parsed as valid JSON: ", e)
            raise ValueError("AI response is not valid JSON.")
        except Exception as e:
            raise RuntimeError(f"AI call for {self.name} failed: {e}")

    async def take_turn(self, history: list) -> dict:
        turn_request_json = {
            "type": "your_turn_to_say_word",
            "history": history,
            "last_event": history[-1] if history else None
        }
        return await self._call_ai(turn_request_json)

    async def take_vote(self, user_message: list) -> dict:
        vote_request_json = {
            "type": "request_vote",
            "history": user_message,
        }
        return await self._call_ai(vote_request_json)

    async def comment_on_turn(self, history: list) -> dict:
        last_event = history[-1] if history else None
        comment_request_json = {
            "type": "request_comment",
            "player_who_said_word": last_event['player'] if last_event else "Unknown",
            "word_just_said": last_event['word'] if last_event and last_event.get("action") == "say_word" else "No word said, maybe someone commented",
            "history": history,
            "last_event": last_event
        }
        return await self._call_ai(comment_request_json)

    async def initialize_on_api(self):
        init_json = {
            "type": "init",
            "role": self.role,
            "language": self.language,
            "secret_word": self.secret_word
        }
        response_data = await self._call_ai(init_json)
        if response_data.get("action") != "confirm_init":
            raise ValueError("Initialization response action is not 'confirm_init'.")
        if not response_data.get("response_text"):
            raise ValueError("Expected a response text, but got nothing.")
        return response_data

    def __str__(self):
        return f"{self.role} {self.name}"
