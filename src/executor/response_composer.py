from schema.tree import (
    SimulatorTree, DecisionNode, AccumulatorNode,
    TerminalSNode, TerminalFNode,
)
from executor.llm_interpretation import interpret
from executor.models import Interpretation
from executor.mock_values import make_mock_state, make_mock_tree, MOCK_USER_INPUT


def main()-> None:
    # Check functions with mock values:
    mock_state = make_mock_state()
    mock_tree = make_mock_tree()
    mock_interpretation = interpret(mock_state, mock_tree, MOCK_USER_INPUT)
    mock_current_node = mock_tree.resolve(mock_state.current_node_ref)

    # print(compose_terminal(mock_current_node))
    print(compose_accumulator_match(mock_current_node, mock_interpretation))


def compose_decision_match(node: DecisionNode, interpretation: Interpretation) -> str:
    assert interpretation.matched_action_index is not None
    return node.expected_actions[interpretation.matched_action_index].feedback


def compose_accumulator_match(node: AccumulatorNode, interpretation: Interpretation) -> str:
    parts = []
    assert interpretation.matched_components != []
    for matched_component in interpretation.matched_components:
        for component_feedback in node.component_feedback:
            if component_feedback.component == matched_component:
                parts.append(f"- ✅ {component_feedback.component.capitalize()} → {component_feedback.feedback}")
                break
    return "\n\n".join(parts)


def compose_hint(node: DecisionNode | AccumulatorNode, hints_used: int) -> str:
    hint_index = min(hints_used, len(node.hints) - 1)
    return f"💡 {node.hints[hint_index]}"


def compose_off_path(tree: SimulatorTree) -> str:
    return f"⚠️ {tree.execution_rules.default_off_path_response}"


def compose_terminal(node: TerminalSNode | TerminalFNode) -> str:
    if isinstance(node, TerminalSNode):
        return (
            f"🎉 {node.feedback_template}\n\n"
            f"🎯 **Diagnosis:** {node.diagnosis}"
        )
    return node.feedback_template  # TerminalFNode has no diagnosis field


if __name__ == "__main__":
    main()
