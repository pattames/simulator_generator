from string import Template
from pathlib import Path
import json

from executor.models import ExecutorState
from schema.tree import SimulatorTree, DecisionNode, AccumulatorNode, TerminalSNode, TerminalFNode
from executor.mock_values import make_mock_tree, make_mock_state, MOCK_USER_INPUT 

def main() -> None:
    # Build user message with pre-written mock values for checking
    mock_tree = make_mock_tree()
    mock_state = make_mock_state()
    mock_current_node = mock_tree.resolve(mock_state.current_node_ref)

    print(serialize_node_actions(mock_current_node))
    print(build_user_message(mock_state, mock_tree, MOCK_USER_INPUT))

# Add the explicit "index" field to decision node's actions to avoid LLM counting errors
def serialize_node_actions(current_node: DecisionNode | AccumulatorNode | TerminalSNode | TerminalFNode) -> str:
    if isinstance(current_node, DecisionNode):
        data = current_node.model_dump()
        for i, action in enumerate(data["expected_actions"]):
            action["index"] = i
        return json.dumps(data, indent=2, ensure_ascii=False)
    return current_node.model_dump_json(indent=2)


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
        current_node=serialize_node_actions(current_node),
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
