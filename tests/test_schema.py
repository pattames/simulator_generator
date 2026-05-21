from pathlib import Path
from schema.tree import SimulatorTree

for example_path in Path("examples").glob("*.json"):
    raw = example_path.read_text()
    tree = SimulatorTree.model_validate_json(raw)
    print(f"✓ {tree.simulator_id}")
