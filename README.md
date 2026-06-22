# Simulator Generator v1

CLI tool built with Python, Pydantic, Groq API and Claude API.

*Note:* Due to the use of third party LLMs, API keys are required.

## Setup

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd simulator_generator
   ```

2. Check if the project's pinned Python version matches yours

   ```bash
   cat .python-version
   ```

3. Create a virtual environment and activate it

   ```bash
   python -m venv .venv && source .venv/bin/activate
   ```

4. Install dependencies

   ```bash
   pip install -r requirements.lock -r requirements-dev.lock
   ```

5. Create environment variables file

   ```bash
   # copy .env.example content and paste to .env while creating it
   cp .env.example .env
   ```

   Then edit `.env` and add your API keys

## Usage

- Run the simulator generator by choosing a domain of your liking and following these examples:

   ```bash
   # From project root:
   python -m app "I want a simulator to diagnose internal combustion engine failures"
   python -m app "A simulator that tests my knowledge on greek mythology"
   
   # In Spanish:
   python -m app "Quiero un simulador para diagnosticar fallas en motores de combustión interna"
   python -m app "Un simulador para poner a prueba mis conocimientos sobre mitología griega"
   ```

- **Important:** When using the previous command, the program can take up to 90 seconds to generate the simulator. After that, interacting with the application is very fast.
- You can exit the program at any time by prompting `/exit` or `/quit`

## Simulator Rules

- There is a limited amount of hints available per every stage, you can ask for one when feeling stuck or the program will give you one automatically if your answer diverges from whats expected.
- Every hint will be marked with a `💡` emoji.
- If the maximum amount of hints per stage is surpassed, the simulator will automatically fail you.
- If your answer is completely off-topic, you'll get a feedback message marked with the `⚠️` emoji. If you exceed the maximum off-topic attempts per session, you'll fail.
