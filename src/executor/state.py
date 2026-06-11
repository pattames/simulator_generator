from pydantic import BaseModel, Field
from typing import Literal

class Penalty(BaseModel):
    node_id: str
    level: Literal["minor", "moderate", "major"]
    note: str       # e.g., for user input that caused the penalty

class ExecutorState(BaseModel):
    current_node_ref: str
    hints_used_this_node: int = 0
    off_path_global_count: int = 0
    accumulator_components_covered: set[str] = Field(default_factory=set)
    penalties: list[Penalty] = Field(default_factory=list)
    conversation_history: list[dict] = Field(default_factory=list)
    is_terminated: bool = False
