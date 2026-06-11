# Mock values for checking other modules
from pathlib import Path
from schema.tree import SimulatorTree
from executor.state import ExecutorState, Penalty

MOCK_USER_INPUT = "Estoy un poco confundido."


def main() -> None:
    print("MOCK TREE:\n", make_mock_tree())
    print("---------------------")
    print("MOCK STATE:\n", make_mock_state())
    print("---------------------")
    print("MOCK USER INPUT:\n", MOCK_USER_INPUT)


def make_mock_tree() -> SimulatorTree:
    raw_mock_tree = Path("examples/arch_generated/cybersecurity.json").read_text()
    mock_tree = SimulatorTree.model_validate_json(raw_mock_tree)

    return mock_tree


def make_mock_state() -> ExecutorState:
    mock_history_state = [
        {"role": "user", "content": "¿Cómo configuro un nodo raíz en el árbol?"},
        {"role": "assistant", "content": "El nodo raíz necesita un id único y una lista de transitions."},
        {"role": "user", "content": "What if a node has no children?"},
        {"role": "assistant", "content": "Then it's a terminal node — mark it with is_terminal=True."},
        {"role": "user", "content": "Can transitions point backwards?"},
        {"role": "assistant", "content": "Yes, the flat structure allows any node to reference any other by id."},
        {"role": "user", "content": "How do I validate the whole tree?"},
        {"role": "assistant", "content": "Run it through the SimulatorTree Pydantic model."},
    ]
    mock_penalty_state_1 = Penalty(
        node_id = "n1",
        level = "major",
        note = "Suggested to pay the ransom in early stages."
    )
    mock_penalty_state_2 = Penalty(
        node_id = "n2",
        level = "moderate",
        note = "Suggested to start the recovery process without controlling the attack first."
    )
    mock_state = ExecutorState(
        current_node_ref = "n2",
        hints_used_this_node = 0,
        # off_path_global_count = 1,
        accumulator_components_covered = {"erradicación y hardening"},
        # penalties = [mock_penalty_state_1, mock_penalty_state_2],
        # conversation_history = mock_history_state,
        # is_terminated = False
    )
    
    return mock_state


if __name__ == "__main__":
    main()
