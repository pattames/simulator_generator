import os
import json
from pydantic import BaseModel, Field
from typing import Literal
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from executor.state import ExecutorState
from schema.tree import SimulatorTree
from executor.user_message import build_user_message, build_mock_user_message

load_dotenv()

# Output structure
class Interpretation(BaseModel):
    classification: Literal["action_match", "hint_needed", "off_path"]
    # For decision nodes:
    matched_action_index: int | None = None
    # For accumulator nodes:
    matched_components: list[str] = Field(default_factory=list)
    # Short reasoning trace, useful for debugging and logging
    reasoning: str | None = None

INTERPRETATION_SYSTEM_PROMPT = Path("executor/system_prompt.md").read_text()
groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def interpret(state: ExecutorState, tree: SimulatorTree, user_input: str) -> Interpretation:
    # User message with arguments designed to come from runner
    user_message = build_user_message(state, tree, user_input)
    # User message with mock values for testing without runner
    mock_user_message = build_mock_user_message()

if __name__ == "__main__":
    print(groq_client)
