from pydantic import BaseModel
from enum import Enum

class PlayerRole(str, Enum):
    CREWMATE = "crewmate"
    IMPOSTER = "imposter"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class CreateLobbyRequest(BaseModel):
    language: str = "en"
    player_name: str
    player_role: PlayerRole
    num_agents: int
    difficulty: Difficulty
