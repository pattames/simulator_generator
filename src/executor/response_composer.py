from schema.tree import (
    SimulatorTree, DecisionNode, AccumulatorNode,
    TerminalSNode, TerminalFNode,
)
from executor.interpretation import Interpretation
from executor.state import ExecutorState


def main()-> None:
    pass


def compose_decision_match(node: DecisionNode, interpretation: Interpretation) -> str:
    assert interpretation.matched_action_index is not None
    return node.expected_actions[interpretation.matched_action_index].feedback


if __name__ == "__main__":
    main()
