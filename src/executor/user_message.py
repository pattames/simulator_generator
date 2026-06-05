from string import Template
from executor.state import ExecutorState, Penalty
from schema.tree import SimulatorTree

def main() -> None:
    # print(check_history_format())
    print(check_user_message())

def check_user_message() -> str:
    mock_history = [
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
        hints_used_this_node = 2,
        # off_path_global_count = 1,
        # accumulator_components_covered = {"erradicación y hardening", "plan de recuperación priorizado"},
        penalties = [mock_penalty_state_1, mock_penalty_state_2],
        conversation_history = mock_history,
        # is_terminated = False
    )

    return mock_state

def build_user_message(state: ExecutorState, tree: SimulatorTree, user_input: str) -> str:
    current_node = tree.resolve(state.current_node_ref)

    return current_node

def check_history_format() -> str:
    mock_history = [
        {"role": "user", "content": "¿Cómo configuro un nodo raíz en el árbol?"},
        {"role": "assistant", "content": "El nodo raíz necesita un id único y una lista de transitions."},
        {"role": "user", "content": "What if a node has no children?"},
        {"role": "assistant", "content": "Then it's a terminal node — mark it with is_terminal=True."},
        {"role": "user", "content": "Can transitions point backwards?"},
        {"role": "assistant", "content": "Yes, the flat structure allows any node to reference any other by id."},
        {"role": "user", "content": "How do I validate the whole tree?"},
        {"role": "assistant", "content": "Run it through the SimulatorTree Pydantic model."},
    ]
    return format_conversation_history(mock_history, last_n=6)

# Shorten and format conversation history for template use
def format_conversation_history(history: list[dict], last_n: int = 6) -> str:
    if not history:
        return "(no prior turns)"
    recent = history[-last_n:]
    lines = [f"- **{turn['role']}:** {turn['content']}" for turn in recent]
    return "\n".join(lines)

if __name__ == "__main__":
    main()
