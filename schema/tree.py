from pydantic import BaseModel

class ExpectedAction(BaseModel):
    action_keywords: list[str]
    feedback: str
    next_node: str
    penalty: str

class DecisionNode(BaseModel):
    node_type: str
    stage: str
    available_info: str
    expected_actions: list[ExpectedAction]
    hints: list[str]

class Nodes(BaseModel):
    decision_node: DecisionNode

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
    learning_objectives: list[str]

class SimulatorTree(BaseModel):
    simulator_id: str
    metadata: Metadata
    presentation: Presentation
    start_node: str
    nodes: Nodes

if __name__ == "__main__":
    import json
    schema = SimulatorTree.model_json_schema()
    print(json.dumps(schema, indent=2))
