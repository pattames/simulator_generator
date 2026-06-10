from string import Template
from executor.state import ExecutorState
from schema.tree import SimulatorTree
from pathlib import Path
from executor.mock_values import make_mock_tree, make_mock_state, MOCK_USER_INPUT 

def main() -> None:
    # Build user message with pre-written mock values for checking
    print(build_user_message(make_mock_state(), make_mock_tree(), MOCK_USER_INPUT))

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
