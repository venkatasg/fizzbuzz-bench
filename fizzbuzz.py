"""
Fizzbuzz Benchmark for LLMs
Uses Simon Willison's LLM library (https://llm.datasette.io/)
Works with any model supported by LLM and its plugins.
"""

import argparse
import os

import llm
from dotenv import load_dotenv
from llm.default_plugins.openai_models import Chat

from utils import get_fizzbuzz_response, log_print

# Maps model name prefixes to the reasoning/thinking option for that provider.
# Each entry is (option_name, value) to pass as a kwarg to prompt().
REASONING_OPTIONS = {
    "claude-": ("thinking_effort", "high"),
    "gemini-": ("thinking_level", "high"),
    "gpt-": ("reasoning_effort", "high"),
}


def is_endpoint(model: str) -> bool:
    """True if --model is a Chat Completions URL rather than an LLM model ID."""
    return model.startswith(("http://", "https://"))


def get_reasoning_kwargs(model_name: str, local: bool = False) -> dict:
    """Return the appropriate reasoning/thinking kwarg for a model, if known."""
    if local:
        # A local model ID tells us nothing, but the endpoint is OpenAI-shaped.
        return {"reasoning_effort": "high"}
    for prefix, (option, value) in REASONING_OPTIONS.items():
        if model_name.startswith(prefix):
            return {option: value}
    return {}


def get_local_model(url: str, reasoning: bool = False) -> tuple[Chat, str]:
    """
    Build a model from a Chat Completions URL (vLLM, llama.cpp, LM Studio,
    Ollama, ...), asking the endpoint which model it serves. Returns the model
    and the served model ID. Append '#model-id' to the URL to pick one when the
    server serves several.
    """
    api_base, _, wanted = url.partition("#")
    api_base = api_base.rstrip("/")

    model = Chat(model_id=url, api_base=api_base, reasoning=reasoning)
    # Chat defaults to needs_key="openai" - never hand OPENAI_API_KEY to some
    # other host. LLM sends a dummy key instead, which is what local servers want.
    # (None is what LLM itself assigns for keyless models; ty only objects because
    # Chat's unannotated `needs_key = "openai"` narrows the declared type to str.)
    model.needs_key = None  # ty: ignore[invalid-assignment]
    api_key = os.environ.get("LOCAL_API_KEY")
    if api_key:
        # Only if the server actually checks the Authorization header.
        model.needs_key = "local"
        model.key = api_key

    # Servers like Ollama mount the OpenAI API under /v1, so try that too.
    bases = [api_base] if api_base.endswith("/v1") else [api_base, api_base + "/v1"]
    served = None
    for base in bases:
        model.api_base = api_base = base
        try:
            served = [m.id for m in model.get_client(None).models.list().data]
            break
        except Exception as e:  # noqa: BLE001 - any failure means "try the next base"
            error = e
    if served is None:
        raise SystemExit(f"Could not reach {bases[0]}: {error}") from error

    if wanted:
        if served and wanted not in served:
            raise SystemExit(
                f"{api_base} does not serve '{wanted}'. Available: {', '.join(served)}"
            )
        model_name = wanted
    elif not served:
        raise SystemExit(f"{api_base} reports no models")
    elif len(served) > 1:
        raise SystemExit(
            f"{api_base} serves several models - pick one by appending '#model-id' "
            f"to the URL. Available: {', '.join(served)}"
        )
    else:
        model_name = served[0]

    model.model_id = model.model_name = model_name
    return model, model_name


def run_fizzbuzz_game(
    model,
    log_file,
    model_name: str,
    fizz_num: int = 3,
    buzz_num: int = 5,
    max_turns: int = 200,
    reasoning: bool = False,
    local: bool = False,
) -> int:
    """
    Run a Fizzbuzz game with an LLM and return the turn number where it failed.
    Returns 0 if it fails on the first turn, or the turn number of the last correct answer.
    """
    log_print(f"Testing {model_name}", log_file)

    with open("SYSTEM_PROMPT.md", "r") as f:
        system_prompt = f.read().strip().format(fizz_num=fizz_num, buzz_num=buzz_num)

    extra_kwargs = get_reasoning_kwargs(model_name, local) if reasoning else {}
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

        except Exception as e:  # noqa: BLE001 - any failure ends the run
            log_print(f"ERROR at turn {turn}: {e}", log_file)
            return turn - 1


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark LLMs on FizzBuzz using the LLM library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fizzbuzz.py --model gpt-4.1 --reasoning
  python fizzbuzz.py --model claude-sonnet-4-5-20250929 --reasoning
  python fizzbuzz.py --model gemini-2.5-flash --reasoning
  python fizzbuzz.py --model deepseek-chat
  python fizzbuzz.py --model deepseek-reasoner
  python fizzbuzz.py --model moonshot/kimi-k2-thinking
  python fizzbuzz.py --model glm-4-plus
  python fizzbuzz.py --model claude-sonnet-4-5-20250929 --fizz 7 --buzz 4 --reasoning

  # Pass a Chat Completions URL to play against a locally served model
  python fizzbuzz.py --model http://localhost:8000/v1
  python fizzbuzz.py --model http://localhost:11434/v1#qwen3:8b --fizz 7 --buzz 4

Note: For DeepSeek reasoning, use the deepseek-reasoner model directly.
      For Kimi reasoning, use moonshot/kimi-k2-thinking model directly.
      Qwen models are available via llm-together or llm-openrouter.
      A URL needs no plugin or API key - the endpoint is asked which model it
      serves. Append '#model-id' if it serves more than one. Set LOCAL_API_KEY
      if the server checks the Authorization header.
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
        help="Model ID (e.g., gpt-4.1, gemini-2.5-flash), or a Chat Completions "
        "URL for a local model (e.g., http://localhost:8000/v1)",
    )
    parser.add_argument(
        "--reasoning",
        action="store_true",
        default=False,
        help="Enable reasoning/thinking mode (sets high effort for supported models)",
    )

    args = parser.parse_args()

    load_dotenv()

    # A URL means a locally served model - ask the endpoint what it is, so the
    # rest of the run (log filename included) uses the real model ID.
    model: llm.Model | Chat
    local = is_endpoint(args.model)
    endpoint = None
    if local:
        model, model_name = get_local_model(args.model, reasoning=args.reasoning)
        endpoint = model.api_base
    else:
        model_name = args.model
        model = llm.get_model(model_name)

    os.makedirs("logs", exist_ok=True)

    # Local model IDs can carry '/' and ':' (e.g. 'qwen3:8b') - keep filenames sane.
    slug = model_name.replace("/", "_").replace(":", "_")
    log_filename = f"logs/{slug}_fizz_{args.fizz_num}_buzz_{args.buzz_num}.log"

    with open(log_filename, "w") as log_file:
        log_print("Fizzbuzz LLM Benchmark", log_file)
        log_print("=" * 60, log_file)
        log_print(f"Model: {model_name}", log_file)
        if endpoint:
            log_print(f"Endpoint: {endpoint}", log_file)
        log_print(f"Game Rules: fizz={args.fizz_num}, buzz={args.buzz_num}", log_file)
        log_print("=" * 60, log_file)

        score = run_fizzbuzz_game(
            model=model,
            log_file=log_file,
            model_name=model_name,
            fizz_num=args.fizz_num,
            buzz_num=args.buzz_num,
            max_turns=args.max_turns,
            reasoning=args.reasoning,
            local=local,
        )

        log_print(f"\n{'=' * 60}", log_file)
        log_print("FINAL RESULTS", log_file)
        log_print(f"Model: {model_name}", log_file)
        log_print(f"Game Rules: fizz={args.fizz_num}, buzz={args.buzz_num}", log_file)
        log_print("=" * 60, log_file)
        log_print(f"{model_name}: {score} correct turns", log_file)
        log_print("=" * 60, log_file)


if __name__ == "__main__":
    main()
