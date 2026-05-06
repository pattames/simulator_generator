from pydantic import BaseModel, Field
from typing import Literal

class ComponentFeedback(BaseModel):
    component: str
    feedback: str

class AccumulatorNode(BaseModel):
    type: Literal["accumulator"]
    stage: str
    available_info: str
    required_components: list[str] = Field(min_length=1)
    component_feedback: list[ComponentFeedback] = Field(min_length=1)
    on_complete: Literal["terminal_success"]
    hints: list[str] = Field(min_length=1)

class ExpectedAction(BaseModel):
    action_keywords: list[str]
    feedback: str
    next: str
    penalty: Literal["minor", "moderate", "mayor"] | None = None

class DecisionNode(BaseModel):
    type: Literal["decision"]
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
    start_node: str
    nodes: dict[str, DecisionNode | AccumulatorNode]

if __name__ == "__main__":
    import json
    schema = SimulatorTree.model_json_schema()
    print(json.dumps(schema, indent=2))
