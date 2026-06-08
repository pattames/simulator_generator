from string import Template
from executor.state import ExecutorState, Penalty
from schema.tree import SimulatorTree
from pathlib import Path

def main() -> None:
    print(build_mock_user_message())

# Build user message with pre-written mock values for checking
def build_mock_user_message() -> str:
    raw_mock_tree = Path("examples/arch_generated/cybersecurity.json").read_text()
    mock_tree = SimulatorTree.model_validate_json(raw_mock_tree)
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
        hints_used_this_node = 2,
        # off_path_global_count = 1,
        accumulator_components_covered = {"erradicación y hardening", "plan de recuperación priorizado"},
        penalties = [mock_penalty_state_1, mock_penalty_state_2],
        conversation_history = mock_history_state,
        # is_terminated = False
    )

    return build_user_message(mock_state, mock_tree, "Estoy atorado, ¿cómo me sugerirías continuar?")

def build_user_message(state: ExecutorState, tree: SimulatorTree, user_input: str) -> str:
    user_message_template = Template(Path("executor/user_message_template.md").read_text())
    current_node = tree.resolve(state.current_node_ref)
    covered_components_str = (
        f"- {'\n- '.join(sorted(state.accumulator_components_covered))}"
        if state.accumulator_components_covered
        else "(none -- not in accumulator node yet, or no components covered)"
    )
    recent_history_str = format_conversation_history(state.conversation_history, last_n=6)

    return user_message_template.substitute(
        hint_path_def=tree.execution_rules.hint_path_def,
        off_path_def=tree.execution_rules.off_path_def,
        current_node=current_node.model_dump_json(indent=2),
        covered_components=covered_components_str,
        conversation_history=recent_history_str,
        user_message=user_input,
    )


def format_conversation_history(history: list[dict], last_n: int = 6) -> str:
    if not history:
        return "(no prior turns)"
    recent = history[-last_n:]
    lines = [f"- **{turn['role']}:** {turn['content']}" for turn in recent]
    return "\n".join(lines)

if __name__ == "__main__":
    main()
