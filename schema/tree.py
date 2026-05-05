from pydantic import BaseModel

class Metadata(BaseModel):
    domain: str
    topic: str
    learning_objectives: list[str]

class SimulatorTree(BaseModel):
    simulator_id: str
    metadata: Metadata

if __name__ == "__main__":
    import json
    schema = SimulatorTree.model_json_schema()
    print(json.dumps(schema, indent=2))
