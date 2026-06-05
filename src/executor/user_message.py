def main() -> None:
    print(check_history_format())

def check_history_format() -> str:
    mock_history = [
        {"role": "user", "content": "¿Cómo configuro un nodo raíz en el árbol?"},
        {"role": "assistant", "content": "El nodo raíz necesita un id único y una lista de transitions."},
        {"role": "user", "content": "What if a node has no children?"},
        {"role": "assistant", "content": "Then it's a terminal node — mark it with is_terminal=True."},
        {"role": "user", "content": "Can transitions point backwards?"},
        {"role": "assistant", "content": "Yes, the flat structure allows any node to reference any other by id."},
        {"role": "user", "content": "How do I validate the whole tree?"},
        {"role": "assistant", "content": "Run it through the SimulatorTree Pydantic model."},
    ]
    return format_conversation_history(mock_history, last_n=6)

# Shorten and format conversation history for template use
def format_conversation_history(history: list[dict], last_n: int = 6) -> str:
    if not history:
        return "(no prior turns)"
    recent = history[-last_n:]
    lines = [f"- **{turn['role']}:** {turn['content']}" for turn in recent]
    return "\n".join(lines)

if __name__ == "__main__":
    main()
