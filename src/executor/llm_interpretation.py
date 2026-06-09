from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field, ValidationError

from executor.state import ExecutorState
from executor.user_message import build_user_message
from executor.mock_values import MOCK_USER_INPUT, make_mock_tree, make_mock_state
from schema.tree import SimulatorTree

load_dotenv()

INTERPRETATION_SYSTEM_PROMPT = Path("executor/system_prompt.md").read_text()
# Multiple LLM call attempts to ensure output structure
MAX_ATTEMPTS = 3

groq_client = Groq()


# Pydantic target output structure
class Interpretation(BaseModel):
    classification: Literal["action_match", "hint_needed", "off_path"]
    # For decision nodes:
    matched_action_index: int | None = None
    # For accumulator nodes:
    matched_components: list[str] = Field(default_factory=list)
    # Short reasoning trace, useful for debugging and logging
    reasoning: str


def main() -> None:
    # Check LLM reponse with mock values
    print(interpret(make_mock_state(), make_mock_tree(), MOCK_USER_INPUT))


def interpret(state: ExecutorState, tree: SimulatorTree, user_input: str) -> Interpretation:
    user_message = build_user_message(state, tree, user_input)

    for attempt in range(MAX_ATTEMPTS):
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": INTERPRETATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content
        if raw is None:
            raise RuntimeError("Empty response from model")
        try:
            return Interpretation.model_validate_json(raw)
        except ValidationError as e:
            # If last attempt, raise the error
            if attempt == MAX_ATTEMPTS - 1:
                raise
            # Append the error to user_message for self-correction on retry
            user_message += f"\n\nYour previous response failed validation: {e}. Return only valid JSON matching the schema."

    # defensive line that never executes but satisfies mypy
    raise RuntimeError("Unreachable")


if __name__ == "__main__":
    main()
