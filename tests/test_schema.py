from pathlib import Path
from schema.tree import SimulatorTree

raw = Path("examples/vet_canine.json").read_text()
tree = SimulatorTree.model_validate_json(raw)
print(f"✓ Loaded {tree.simulator_id} ({len(tree.nodes)} nodes)")
