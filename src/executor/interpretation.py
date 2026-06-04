from pydantic import BaseModel, Field
from typing import Literal
from pathlib import Path

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

if __name__ == "__main__":
    print(INTERPRETATION_SYSTEM_PROMPT)
