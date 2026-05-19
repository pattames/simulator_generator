from pydantic import BaseModel, Field
from typing import Literal

class ExecutionRules(BaseModel):
    hint_path_def: Literal["The user is engaged with the case but stuck — they're reasoning incorrectly, reasoning incompletely, asking for help, or requesting clarification about case details"]
    max_hints_per_node: int = Field(ge=1)
    off_path_def: Literal["The user's message is entirely unrelated to the case"]
    default_off_path_response: str
    off_path_max_attempts: int = Field(ge=1)

class TerminalFNode(BaseModel):
    outcome: Literal["failure"]
    feedback_template: str

class TerminalSNode(BaseModel):
    outcome: Literal["success"]
    diagnosis: str
    feedback_template: str

class ComponentFeedback(BaseModel):
    component: str
    feedback: str

class AccumulatorNode(BaseModel):
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
    id: str
    stage: str
    available_info: str
    expected_actions: list[ExpectedAction] = Field(min_length=1)
    hints: list[str] = Field(min_length=1)

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
    decision_nodes: list[DecisionNode] = Field(
        min_length=2,
        description="Ordered list of 3-5 decision nodes representing the case's reasoning stages."
    )
    accumulator: AccumulatorNode
    terminal_success: TerminalSNode
    termina_failure: TerminalFNode
    execution_rules: ExecutionRules

if __name__ == "__main__":
    import json
    schema = SimulatorTree.model_json_schema()
    print(json.dumps(schema, indent=2))
