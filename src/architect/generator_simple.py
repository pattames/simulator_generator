from pathlib import Path
from string import Template
from anthropic import Anthropic
from schema.tree_simple import SimulatorTree
from dotenv import load_dotenv

load_dotenv()

prompt_template = Template(Path("src/architect/prompt.md").read_text())
ARCHITECT_SYSTEM_PROMPT = prompt_template.substitute(
    auto_example=Path("examples/auto_fuel_pump.json").read_text(),
    vet_example=Path("examples/vet_canine.json").read_text(),
)

client = Anthropic()

def generate_tree(user_description: str) -> SimulatorTree:
    response = client.messages.parse(
        model="claude-sonnet-4-6",
        max_tokens=16000,        # set high to avoid incomplete trees
        system=ARCHITECT_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"{user_description}"
            }
        ],
        output_format=SimulatorTree,
    )
    return response.parsed_output

# To test with user prompt as CLI's argument
if __name__ == "__main__":
    import sys
    import json

    user_prompt = sys.argv[1]

    tree = generate_tree(user_prompt)
    print(json.dumps(tree.model_dump(), indent=2, ensure_ascii=False))
