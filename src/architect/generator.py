from pathlib import Path
from string import Template
from anthropic import Anthropic
from pydantic import ValidationError
from schema.tree import SimulatorTree
from dotenv import load_dotenv
import json

load_dotenv()

prompt_template = Template(Path("src/architect/prompt.md").read_text())
ARCHITECT_SYSTEM_PROMPT = prompt_template.substitute(
    auto_example=Path("examples/auto_fuel_pump.json").read_text(),
    vet_example=Path("examples/vet_canine.json").read_text(),
)

client = Anthropic()

# With multiple attempts to ensure structure and validation against Pydantic's schema
def generate_tree(user_description: str, max_attempts: int = 3) -> SimulatorTree:
    last_error = None

    for attempt in range(max_attempts):
        messages = [{"role": "user", "content": user_description}]
        if last_error:
            messages.append({
                "role": "user",
                "content": (
                    f"The previous tree failed validation with this error:\n"
                    f"{last_error}\n\nPlease produce a corrected tree."
                )
            })
        try:
            response = client.messages.parse(
                model="claude-haiku-4-5",
                max_tokens=16000,        # set high to avoid incomplete trees
                system=ARCHITECT_SYSTEM_PROMPT,
                messages=messages,
                output_format=SimulatorTree,
            )
        except ValidationError as e:
            last_error = str(e)
            continue
        parsed = response.parsed_output
        if parsed is None:
            last_error = "Model did not return a parseable tree, it doesn't match Pydantic's schema."
            continue
        return parsed

    raise RuntimeError(f"Architect failed after {max_attempts} attempts: {last_error}")

# To test with user prompt as CLI's argument
if __name__ == "__main__":
    import sys

    # Avoid index error if argument not provided
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else input("Pide el simulador que deseas")

    tree = generate_tree(user_prompt)
    print(json.dumps(tree.model_dump(), indent=2, ensure_ascii=False))
