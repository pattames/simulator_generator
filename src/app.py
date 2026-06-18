import sys
import json

from architect.generator import generate_tree

def main() -> None:
    # Handle user prompt
    if len(sys.argv) != 2:
        print("Program needs a single prompt to be passed as an argument")
        sys.exit(1)
    user_prompt = sys.argv[1]

    # Handle tree generation
    try:
        tree = generate_tree(user_prompt)
    except Exception:
        print("Tree not generated properly, try reformulating your prompt")
        sys.exit(1)

    if tree is None or tree.simulator_id is None:
        print("Invalid instruction, please try with a valid prompt")
        sys.exit(1)

    # Tree presentation
    print(f"\n{'-' * 15} YOUR SIMULATOR: {'-' * 15}\n")
    print(f"• Domain: {tree.metadata.domain}")
    print(f"• Topic: {tree.metadata.topic}")
    
    print(json.dumps(tree.model_dump(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
