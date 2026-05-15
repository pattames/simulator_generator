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
