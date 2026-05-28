from pathlib import Path
import json

def main() -> None:
    tree_example_str = Path("examples/arch_generated/cybersecurity.json").read_text()
    tree_example_dict = json.loads(tree_example_str)
    next_node_str = tree_example_dict["decision_nodes"][1]["expected_actions"][1]["next"]

    print(get_node(next_node_str, tree_example_dict))

def get_node(node_str: str, tree: dict) -> dict:
    # For a decision node
    if len(node_str) == 2:
        for decision_node in tree["decision_nodes"]:
            if decision_node["id"] == node_str:
                return decision_node
    # For an accumulator or terminal node
    return tree[node_str]

if __name__ == "__main__":
    main()
