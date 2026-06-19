import sys

from dotenv import load_dotenv
from groq import Groq

from architect.generator import generate_tree
from executor.runner import run_simulator

load_dotenv()
groq_client = Groq()


def main() -> None:
    # Handle user prompt
    if len(sys.argv) != 2:
        print("Program needs a single prompt to be passed as an argument")
        sys.exit(1)
    user_prompt = sys.argv[1]

    if not validate_simulator_request(user_prompt):
        print("Your prompt doesn't appear to be a simulator request.")
        sys.exit(1)

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


SYSTEM_PROMPT = """Your job is to determine whether a user's message expresses intent to obtain a simulator about some topic or domain. Polite phrasings, indirect requests, conditional phrasings ("could you...", "I'd like...", "would it be possible..."), and direct commands all count as "yes" if the user's underlying intent is to receive a simulator.

Examples:
- "I want a simulator for legal case analysis" → yes
- "Could you generate a simulator about veterinary cases?" → yes
- "Podrías generar un simulador sobre un caso veterinario?" → yes
- "Quiero un simulador para diagnosticar problemas en motores" → yes
- "Make me a training simulator for incident response" → yes
- "What's the capital of France?" → no
- "Tell me a joke" → no
- "Hello, how are you?" → no
- "Explain quantum mechanics to me" → no

Answer with exactly one word: "yes" or "no". Nothing else."""


def validate_simulator_request(user_prompt: str) -> bool:
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0,
        max_tokens=5,
    )

    raw = response.choices[0].message.content
    if raw is None:
        raise RuntimeError("Empty validator response")
    
    return raw.strip().lower().startswith("y")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(130)
