from pathlib import Path
from string import Template
from anthropic import Anthropic
from pydantic import ValidationError
from schema.tree import SimulatorTree

prompt_template = Template(Path("src/architect/prompt.md").read_text())
ARCHITECT_SYSTEM_PROMPT = prompt_template.substitute(
    auto_example=Path("examples/auto_fuel_pump.json").read_text(),
    vet_example=Path("examples/vet_canine.json").read_text(),
)

client = Anthropic()

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
        response = client.messages.parse(
            model="claude-haiku-4-5",
            max_tokens=1600,        # set high to avoid incomplete trees
            system=ARCHITECT_SYSTEM_PROMPT,
            messages=messages,
            output_format=SimulatorTree,
        )
        try:
            return SimulatorTree.model_validate(response.parsed_output.model_dump())
        except ValidationError as e:
            last_error = str(e)

    raise RuntimeError(f"Architect failed after {max_attempts} attempts: {last_error}")
