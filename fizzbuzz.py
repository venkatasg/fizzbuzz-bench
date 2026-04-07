"""
Fizzbuzz Benchmark for LLMs
Uses Simon Willison's LLM library (https://llm.datasette.io/)
Works with any model supported by LLM and its plugins.
"""

import argparse
import os

import llm
from dotenv import load_dotenv

from utils import get_fizzbuzz_response, log_print

# Maps model name prefixes to the reasoning/thinking option for that provider.
# Each entry is (option_name, value) to pass as a kwarg to prompt().
REASONING_OPTIONS = {
    "claude-": ("thinking_effort", "high"),
    "gemini-": ("thinking_level", "high"),
    "gpt-": ("reasoning_effort", "high"),
    "o1": ("reasoning_effort", "high"),
    "o3": ("reasoning_effort", "high"),
    "o4": ("reasoning_effort", "high"),
}


def get_reasoning_kwargs(model_name: str) -> dict:
    """Return the appropriate reasoning/thinking kwarg for a model, if known."""
    for prefix, (option, value) in REASONING_OPTIONS.items():
        if model_name.startswith(prefix):
            return {option: value}
    return {}


def run_fizzbuzz_game(
    model,
    log_file,
    model_name: str,
    fizz_num: int = 3,
    buzz_num: int = 5,
    max_turns: int = 200,
    reasoning: bool = False,
) -> int:
    """
    Run a Fizzbuzz game with an LLM and return the turn number where it failed.
    Returns 0 if it fails on the first turn, or the turn number of the last correct answer.
    """
    log_print(f"Testing {model_name}", log_file)

    with open("SYSTEM_PROMPT.md", "r") as f:
        system_prompt = f.read().strip().format(fizz_num=fizz_num, buzz_num=buzz_num)

    extra_kwargs = get_reasoning_kwargs(model_name) if reasoning else {}
    conversation = model.conversation()

    log_print("Turn 1: User said 1", log_file)
    turn = 2  # LLM should respond with turn 2
    user_message = "1"

    while True:
        try:
            response = conversation.prompt(
                user_message, system=system_prompt, **extra_kwargs
            )
            llm_response = response.text()

            expected = get_fizzbuzz_response(turn, fizz_num, buzz_num)

            log_print(
                f"Turn {turn}: LLM said '{llm_response}' (expected '{expected}')",
                log_file,
            )

            # Normalize responses for comparison (case-insensitive)
            llm_normalized = llm_response.lower().strip()
            expected_normalized = expected.lower().strip()

            if llm_normalized != expected_normalized:
                log_print(f"FAILED at turn {turn}!", log_file)
                log_print(f"Expected: {expected}", log_file)
                log_print(f" Got: {llm_response}", log_file)
                return turn - 1

            turn += 1
            user_message = get_fizzbuzz_response(turn, fizz_num, buzz_num)
            log_print(f"Turn {turn}: User said '{user_message}'", log_file)
            turn += 1

            if turn > max_turns:
                return max_turns

        except Exception as e:
            log_print(f"ERROR at turn {turn}: {e}", log_file)
            return turn - 1


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark LLMs on FizzBuzz using the LLM library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Requires the 'llm' library and appropriate plugins:
  pip install llm                    # OpenAI models (built-in)
  pip install llm-anthropic          # Anthropic Claude models
  pip install llm-gemini             # Google Gemini models
  pip install llm-together           # Together AI (Llama, Qwen, etc.)
  pip install llm-openrouter         # OpenRouter (many providers)
  pip install llm-mistral            # Mistral models
  pip install llm-deepseek           # DeepSeek models
  pip install llm-moonshot           # Kimi/Moonshot models
  pip install llm-zhipu              # GLM/Zhipu models

API keys can be set via:
  llm keys set openai
  llm keys set anthropic
  llm keys set gemini
  llm keys set together
  llm keys set deepseek
  llm keys set moonshot
  llm keys set zhipu
  ...or via environment variables (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)

Examples:
  python fizzbuzz.py --model gpt-4.1 --reasoning
  python fizzbuzz.py --model claude-sonnet-4-5-20250929 --reasoning
  python fizzbuzz.py --model gemini-2.5-flash --reasoning
  python fizzbuzz.py --model deepseek-chat
  python fizzbuzz.py --model deepseek-reasoner
  python fizzbuzz.py --model moonshot/kimi-k2-thinking
  python fizzbuzz.py --model glm-4-plus
  python fizzbuzz.py --model claude-sonnet-4-5-20250929 --fizz 7 --buzz 4 --reasoning

Note: For DeepSeek reasoning, use the deepseek-reasoner model directly.
      For Kimi reasoning, use moonshot/kimi-k2-thinking model directly.
      Qwen models are available via llm-together or llm-openrouter.
        """,
    )
    parser.add_argument(
        "--fizz",
        type=int,
        default=3,
        dest="fizz_num",
        help="Number for 'fizz' (default: 3)",
    )
    parser.add_argument(
        "--buzz",
        type=int,
        default=5,
        dest="buzz_num",
        help="Number for 'buzz' (default: 5)",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=200,
        dest="max_turns",
        help="Maximum number of turns to run game for",
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model ID (e.g., gpt-4.1, claude-sonnet-4-5-20250929, gemini-2.5-flash)",
    )
    parser.add_argument(
        "--reasoning",
        action="store_true",
        default=False,
        help="Enable reasoning/thinking mode (sets high effort for supported models)",
    )

    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)

    log_filename = f"logs/{args.model.replace('/', '_')}_fizz_{args.fizz_num}_buzz_{args.buzz_num}.log"
    log_file = open(log_filename, "w")

    log_print("Fizzbuzz LLM Benchmark", log_file)
    log_print("=" * 60, log_file)
    log_print(f"Model: {args.model}", log_file)
    log_print(f"Game Rules: fizz={args.fizz_num}, buzz={args.buzz_num}", log_file)
    log_print("=" * 60, log_file)

    load_dotenv()
    model = llm.get_model(args.model)

    score = run_fizzbuzz_game(
        model=model,
        log_file=log_file,
        model_name=args.model,
        fizz_num=args.fizz_num,
        buzz_num=args.buzz_num,
        max_turns=args.max_turns,
        reasoning=args.reasoning,
    )

    log_print(f"\n{'=' * 60}", log_file)
    log_print("FINAL RESULTS", log_file)
    log_print(f"Model: {args.model}", log_file)
    log_print(f"Game Rules: fizz={args.fizz_num}, buzz={args.buzz_num}", log_file)
    log_print("=" * 60, log_file)
    log_print(f"{args.model}: {score} correct turns", log_file)
    log_print("=" * 60, log_file)

    log_file.close()


if __name__ == "__main__":
    main()
