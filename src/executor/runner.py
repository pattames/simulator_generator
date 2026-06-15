import json
from datetime import datetime
from pathlib import Path

from schema.tree import (
    SimulatorTree, DecisionNode, AccumulatorNode,
    TerminalSNode, TerminalFNode,
)
from executor.models import ExecutorState, Penalty
from executor.llm_interpretation import interpret
from executor.response_composer import (
    compose_decision_match, compose_accumulator_match,
    compose_hint, compose_off_path, compose_terminal,
)
from executor.mock_values import make_mock_tree
# from executor.mock_values import make_mock_state, MOCK_USER_INPUT


def main()-> None:
    # Check with mock values:
    # mock_state = make_mock_state()
    mock_tree = make_mock_tree()
    # mock_current_node = mock_tree.resolve(mock_state.current_node_ref)

    # print(process_turn(MOCK_USER_INPUT, mock_state, mock_tree))
    # print_presentation(mock_tree)
    # print_node_intro(mock_current_node)
    # save_session(mock_state, mock_tree)
    run_simulator(mock_tree)


def process_turn(user_input: str, state: ExecutorState, tree: SimulatorTree) -> ExecutorState:
    # Pre-transition values
    node_before = tree.resolve(state.current_node_ref)
    assert not isinstance(node_before, (TerminalSNode, TerminalFNode)), "process_turn should not be called when current node is terminal"
    hints_used_before = state.hints_used_this_node

    # 1. Classify the user's input
    llm_interpretation = interpret(state, tree, user_input)
    # Add interpretation to state
    state.llm_interpretations.append(llm_interpretation)

    # 2. Apply new state transitions
    response: str

    if llm_interpretation.classification == "action_match":
        # If there is a decision node action match
        if isinstance(node_before, DecisionNode):
            assert llm_interpretation.matched_action_index is not None, "matched_action_index must be set when classification is action_match on a decision node"
            action = node_before.expected_actions[llm_interpretation.matched_action_index]
            state.current_node_ref = action.next
            if node_before.id != action.next:
                state.hints_used_this_node = 0
            if action.penalty is not None:
                state.penalties.append(Penalty(
                    node_id=node_before.id,
                    level=action.penalty,
                    note=f"User input: {user_input[:200]}",  # truncate for log compactness
                ))
            response = compose_decision_match(node_before, llm_interpretation)

        # If there is an accumulator component match
        if isinstance(node_before, AccumulatorNode):
            state.accumulator_components_covered.update(llm_interpretation.matched_components)
            response = compose_accumulator_match(node_before, llm_interpretation)
            # Completion if all components are covered
            if set(node_before.required_components).issubset(state.accumulator_components_covered):
                state.current_node_ref = node_before.on_complete
                state.hints_used_this_node = 0
                # Append terminal-success message after component feedback
                terminal_node = tree.resolve(state.current_node_ref)
                assert isinstance(terminal_node, TerminalSNode)
                response += "\n\n" + compose_terminal(terminal_node)
                state.is_terminated = True

    # If a hint is needed
    elif llm_interpretation.classification == "hint_needed":
        state.hints_used_this_node += 1
        # Terminal failure if number of hints rebases maximum
        if state.hints_used_this_node > tree.execution_rules.max_hints_per_node:
            state.current_node_ref = "terminal_failure"
            terminal_node = tree.resolve(state.current_node_ref)
            assert isinstance(terminal_node, TerminalFNode)
            response = compose_terminal(terminal_node)
            state.is_terminated = True
        else:
            response = compose_hint(node_before, hints_used_before)

    # If going off_path
    elif llm_interpretation.classification == "off_path":
        state.off_path_global_count += 1
        # Terminal failure if number of hints rebases maximum
        if state.off_path_global_count > tree.execution_rules.off_path_max_attempts:
            state.current_node_ref = "terminal_failure"
            terminal_node = tree.resolve(state.current_node_ref)
            assert isinstance(terminal_node, TerminalFNode)
            response = compose_terminal(terminal_node)
            state.is_terminated = True
        else:
            response = compose_off_path(tree)

    # 3. Log the turn in conversation history
    state.conversation_history.append({"role": "user", "content": user_input})
    state.conversation_history.append({"role": "assistant", "content": response})

    return state


def print_presentation(tree: SimulatorTree) -> None:
    p = tree.presentation
    print(f"\n{'=' * 15} CASE PRESENTATION {'=' * 15}\n")
    print(p.intro)
    print()
    for item in p.context:
        print(f" - {item.label}: {item.value}")
    print()
    print(f"{p.initial_prompt}\n")


def print_node_intro(node: DecisionNode | AccumulatorNode) -> None:
    print(f"\n{'-' * 15} STAGE: {node.stage} {'-' * 15}\n")
    print(f"AVAILABLE INFO: {node.available_info}")
    print()


def save_session(state: ExecutorState, tree: SimulatorTree) -> None:
    # Create dir
    log_dir = Path("sessions")
    log_dir.mkdir(exist_ok=True)
    # Create file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = log_dir / f"{tree.simulator_id}_{timestamp}.json"
    path.write_text(
        json.dumps({
            "simulator_id": tree.simulator_id,
            "final_node": state.current_node_ref,
            "hint_count_on_final_node": state.hints_used_this_node,
            "penalties": [penalty.model_dump() for penalty in state.penalties],
            "off_path_count": state.off_path_global_count,
            "accumulator_components_covered": list(state.accumulator_components_covered),
            "history": state.conversation_history,
            "llm_interpretations": [interpretation.model_dump() for interpretation in state.llm_interpretations]
        }, indent=2, ensure_ascii=False)
    )
    print(f"\n(session saved to {path})")


# Simulator runner
def run_simulator(tree: SimulatorTree) -> None:
    state = ExecutorState(current_node_ref="n1")
    print_presentation(tree)
    previous_node_ref = None

    while not state.is_terminated:
        current_node = tree.resolve(state.current_node_ref)

        # Only print node intro when entering a new node
        if state.current_node_ref != previous_node_ref and isinstance(current_node, (DecisionNode, AccumulatorNode)):
            print_node_intro(current_node)

        user_input = input("> ").strip()
        # Handle empty string by re-prompting the user
        if not user_input:
            continue
        if user_input.lower() in {"/quit", "/exit"}:
            print("Session terminated by user.")
            break

        state = process_turn(user_input, state, tree)
        # The last item in conversation_history is the composed response
        print(f"\n{state.conversation_history[-1]['content']}\n")

    save_session(state, tree)


if __name__ == "__main__":
    main()
