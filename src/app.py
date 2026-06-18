import sys

from architect.generator import generate_tree
from executor.runner import run_simulator


def main() -> None:
    # Handle user prompt
    if len(sys.argv) != 2:
        print("Program needs a single prompt to be passed as an argument")
        sys.exit(1)
    user_prompt = sys.argv[1]

    # Handle tree generation
    try:
        tree = generate_tree(user_prompt)
    except Exception as e:
        print(f"Tree not generated properly: {e}")
        print("Try reformulating your prompt.")
        sys.exit(1)

    if tree is None:
        print("Tree generation returned no result. Try again.")
        sys.exit(1)

    # Tree presentation
    print(f"\n{'-' * 15} YOUR SIMULATOR: {'-' * 15}\n")
    print(f"• Domain: {tree.metadata.domain}")
    print(f"• Topic: {tree.metadata.topic}")
    print("• Learning Objectives:")
    for objective in tree.metadata.learning_objectives:
        print(f"    - {objective}")
    print()
    
    # Choice to continue or exit
    choice = input("[c]ontinue or [q]uit? ").strip().lower()
    if choice != "c":
        sys.exit(0)

    # Execute simulator
    run_simulator(tree)


if __name__ == "__main__":
    main()
