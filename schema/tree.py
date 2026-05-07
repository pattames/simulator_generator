from pydantic import BaseModel, Field
from typing import Literal, Annotated

class ExecutionRules(BaseModel):
    hint_path_def: str
    max_hints_per_node: int
    on_excessive_hints: str
    off_path_def: str
    default_off_path_response: str
    off_path_max_attempts: int
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
    action_keywords: list[str]
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

if __name__ == "__main__":
    import json
    schema = SimulatorTree.model_json_schema()
    print(json.dumps(schema, indent=2))
