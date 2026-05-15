from pydantic import BaseModel, Field, model_validator
from typing import Literal, Annotated, Self

class ExecutionRules(BaseModel):
    hint_path_def: Literal["The user is engaged with the case but stuck — they're reasoning incorrectly, reasoning incompletely, asking for help, or requesting clarification about case details"]
    max_hints_per_node: int = Field(ge=1)
    on_excessive_hints: str
    off_path_def: Literal["The user's message is entirely unrelated to the case"]
    default_off_path_response: str
    off_path_max_attempts: int = Field(ge=1)
    on_excessive_off_path: str

class TerminalNode(BaseModel):
    type: Literal["terminal"]
    outcome: Literal["success", "failure"]
    diagnosis: str | None = None
    feedback_template: str

class ComponentFeedback(BaseModel):
    component: str
    feedback: str

class AccumulatorNode(BaseModel):
    type: Literal["accumulator"]
    stage: str
    available_info: str
    required_components: list[str] = Field(min_length=1)
    component_feedback: list[ComponentFeedback] = Field(min_length=1)
    on_complete: str
    hints: list[str] = Field(min_length=1)

class ExpectedAction(BaseModel):
    action_keywords: list[str] = Field(min_length=1)
    feedback: str
    next: str
    penalty: Literal["minor", "moderate", "major"] | None = None

class DecisionNode(BaseModel):
    type: Literal["decision"]
    stage: str
    available_info: str
    expected_actions: list[ExpectedAction] = Field(min_length=1)
    hints: list[str] = Field(min_length=1)

# Look at the node's type field first, then parse into the matching class
NodeUnion = Annotated[
    DecisionNode | AccumulatorNode | TerminalNode,
    Field(discriminator="type")
]

class ContextItem(BaseModel):
    label: str
    value: str

class Presentation(BaseModel):
    intro: str
    context: list[ContextItem]
    initial_prompt: str

class Metadata(BaseModel):
    domain: str
    topic: str
    learning_objectives: list[str] = Field(min_length=1)

class SimulatorTree(BaseModel):
    simulator_id: str
    metadata: Metadata
    presentation: Presentation
    start_node: str
    nodes: dict[str, NodeUnion]
    execution_rules: ExecutionRules

    @model_validator(mode="after")
    def validate_node_structure(self) -> Self:
        # Count node types
        decision_count = sum(1 for n in self.nodes.values() if isinstance(n, DecisionNode))
        accumulator_count = sum(1 for n in self.nodes.values() if isinstance(n, AccumulatorNode))
        success_count = sum(
            1 for n in self.nodes.values()
            if isinstance(n, TerminalNode) and n.outcome == "success"
        )
        failure_count = sum(
            1 for n in self.nodes.values()
            if isinstance(n, TerminalNode) and n.outcome == "failure"
        )

        # Make sure there's at least 1 decision node, but exactly 1 accumulator, 1 success and 1 failure
        if decision_count < 1:
            raise ValueError("Tree must contain at least one decision node")
        if accumulator_count != 1:
            raise ValueError(f"Tree must contain exactly 1 accumulator node, found {accumulator_count}")
        if success_count != 1:
            raise ValueError(f"Tree must contain exactly 1 terminal_success node, found {success_count}")
        if failure_count != 1:
            raise ValueError(f"Tree must contain exactly 1 terminal_failure node, found {failure_count}")

        return self

    @model_validator(mode="after")
    def check_referential_integrity(self) -> Self:
        # Node ids
        node_ids = set(self.nodes.keys())
        decision_node_ids = {nid for nid, n in self.nodes.items() if isinstance(n, DecisionNode)}
        success_node_id = {
            nid for nid, n in self.nodes.items()
            if isinstance(n, TerminalNode) and n.outcome == "success"
        }
        failure_node_id = {
            nid for nid, n in self.nodes.items()
            if isinstance(n, TerminalNode) and n.outcome == "failure"
        }

        # Start node must match a decision node
        if self.start_node not in decision_node_ids:
            raise ValueError(f"start_node '{self.start_node}' must be an existent decision node")

        # Execution rules targets must match the terminal failure node
        if self.execution_rules.on_excessive_hints not in failure_node_id:
            raise ValueError("on_excessive_hints must match the terminal failure node")
        if self.execution_rules.on_excessive_off_path not in failure_node_id:
            raise ValueError("on_excessive_off_path must match the terminal failure node")

        for node_id, node in self.nodes.items():
            # Decision node's next target must exist
            if isinstance(node, DecisionNode):
                for action in node.expected_actions:
                    if action.next not in node_ids:
                        raise ValueError(
                            f"Node '{node_id}' has action with next='{action.next}' which does not exist"
                        )
            elif isinstance(node, AccumulatorNode):
                # Accumulator's required_components must match component_feedback
                required = set(node.required_components)
                provided = {cf.component for cf in node.component_feedback}
                missing = required - provided
                extra = provided - required
                if missing:
                    raise ValueError(
                        f"node '{node_id}': missing component_feedback for {missing}"
                    )
                if extra:
                    raise ValueError(
                        f"node '{node_id}': component_feedback has unexpected "
                        f"entries {extra}"
                    )
                # Accumulator node's on_complete target must match success node
                if node.on_complete not in success_node_id:
                    raise ValueError(
                        f"Node '{node_id}' has on_complete='{node.on_complete}' which does not match the terminal success node"
                    )

        return self

if __name__ == "__main__":
    import json
    schema = SimulatorTree.model_json_schema()
    print(json.dumps(schema, indent=2))
