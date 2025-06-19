from openai import OpenAI
import json

class Player:
    def __init__(self, name: str, ai_client: OpenAI, sysprompt: str):
        if not name or not ai_client or not sysprompt:
            raise ValueError("Name, AI client, and system prompt must be provided.")
        self.name = name
        self.ai_client = ai_client
        self.sysprompt = sysprompt

        self.conversation_history = [{"role": "system", "content": self.sysprompt}]
        self.role = "Not assigned"

    def _call_ai(self, user_message: dict) -> dict:
        self.conversation_history.append({"role": "user", "content": json.dumps(user_message)})
        try:
            response = self.ai_client.chat.completions.create(
                model="x-ai/grok-3-mini-beta",
                messages=self.conversation_history,
                response_format={"type": "json_object"},
            )
            ai_message = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": ai_message})
            return json.loads(ai_message)
        except json.JSONDecodeError as e:
            print("AI response could not be parsed as valid JSON: ", e)
            raise ValueError("AI response is not valid JSON.")
        except Exception as e:
            raise RuntimeError(f"AI call failed: {e}")

    def take_turn(self, user_message: list) -> dict:
        turn_request_json = {
            "type": "your_turn_to_say_word",
            "history": user_message,
            "last_event": user_message[-1] if user_message else None
        }

        return self._call_ai(turn_request_json)