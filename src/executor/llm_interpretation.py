import os
import json
from pydantic import BaseModel, Field
from typing import Literal
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
from executor.state import ExecutorState
from schema.tree import SimulatorTree

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
    pass

if __name__ == "__main__":
    print(groq_client)
