import sys
import json
from pathlib import Path
from string import Template
from datetime import datetime

from anthropic import Anthropic
from dotenv import load_dotenv

from schema.tree import SimulatorTree

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
                "content": user_description
            }
        ],
        output_format=SimulatorTree,
    )
    tree = response.parsed_output
    if tree is None:
        raise RuntimeError("Tree generation returned no result. Try again.")
    save_tree(tree)
    return tree


def save_tree(tree: SimulatorTree) -> None:
    # Create dir
    tree_dir = Path("generated_trees")
    tree_dir.mkdir(exist_ok=True)
    # Create file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = tree_dir / f"{tree.simulator_id}_{timestamp}.json"
    path.write_text(json.dumps(tree.model_dump(), indent=2, ensure_ascii=False))
    print(f"\n(Decision tree saved to {path})")


# To test with user prompt as CLI's argument
if __name__ == "__main__":
    # Handle user prompt
    if len(sys.argv) != 2:
        print("Program needs a single prompt to be passed as an argument")
        sys.exit(1)
    user_prompt = sys.argv[1]

    # Handle tree
    tree = generate_tree(user_prompt)
    if tree is None:
        print("Tree wasn't generated properly")
        sys.exit(1)

    print(json.dumps(tree.model_dump(), indent=2, ensure_ascii=False))
