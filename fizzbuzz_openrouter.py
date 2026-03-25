"""
Fizzbuzz Benchmark for LLMs - OpenRouter API
Uses OpenRouter to access any available model through their unified API.
"""

import argparse
import os
import requests
import json
from utils import log_print, get_fizzbuzz_response
import ipdb


def run_fizzbuzz_game(
    api_key: str,
    log_file,
    model_name: str,
    fizz_num: int = 3,
    buzz_num: int = 5,
    max_turns: int = 100,
) -> int:
    """
    Run a Fizzbuzz game with an LLM via OpenRouter and return the turn number where it failed.
    Returns 0 if it fails on the first turn, or the turn number of the last correct answer.
    """
    log_print(f"Testing {model_name}", log_file)

    with open("SYSTEM_PROMPT.md", "r") as f:
        system_prompt = f.read().strip().format(fizz_num=fizz_num, buzz_num=buzz_num)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "1"},
    ]

    log_print("Turn 1: User said 1", log_file)
    turn = 2  # LLM should respond with turn 2
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/fizzbuzz-bench",
        "X-Title": "FizzBuzz Benchmark",
    }

    while True:
        try:
            payload = {
                "model": model_name,
                "messages": messages,
                "reasoning": {"enabled": True},
            }

            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()

            response = response.json()
            llm_response = response["choices"][0]["message"]["content"]
            ipdb.set_trace()
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

            messages.append(
                {
                    "role": "assistant",
                    "content": response.get("content"),
                    "reasoning_details": response.get("reasoning_details"),
                }
            )

            turn += 1
            user_response = get_fizzbuzz_response(turn, fizz_num, buzz_num)
            messages.append({"role": "user", "content": user_response})

            log_print(f"Turn {turn}: User said '{user_response}'", log_file)

            turn += 1

            if turn > max_turns:
                return max_turns

        except requests.exceptions.HTTPError as e:
            log_print(f"HTTP ERROR at turn {turn}: {e}", log_file)
            if response.text:
                log_print(f"Response: {response.text}", log_file)
            return turn - 1
        except Exception as e:
            log_print(f"ERROR at turn {turn}: {e}", log_file)
            return turn - 1


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark LLMs on FizzBuzz using OpenRouter API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fizzbuzz_openrouter.py --model openai/gpt-5.2
  python fizzbuzz_openrouter.py --model anthropic/claude-sonnet-4-5
  python fizzbuzz_openrouter.py --model google/gemini-2.5-pro --fizz 2 --buzz 7

Note: Model names should include the provider prefix (e.g., openai/, anthropic/, google/)
Visit https://openrouter.ai/models to see all available models.
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
        default=100,
        dest="max_turns",
        help="Maximum number of turns to run game for",
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model to use (e.g., openai/gpt-5.2, anthropic/claude-sonnet-4-5)",
    )

    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)

    log_filename = f"logs/{args.model.replace('/', '_')}_fizz_{args.fizz_num}_buzz_{args.buzz_num}.log"
    log_file = open(log_filename, "w")

    log_print("Fizzbuzz LLM Benchmark - OpenRouter API", log_file)
    log_print("=" * 60, log_file)
    log_print(f"Model: {args.model}", log_file)
    log_print(f"Game Rules: fizz={args.fizz_num}, buzz={args.buzz_num}", log_file)
    log_print("=" * 60, log_file)

    # Read OpenRouter API key
    try:
        with open("../../Research/openrouter-fizzbuzz.txt", "r") as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        log_print(
            "ERROR: Could not find API key file at ../../Research/openrouter-fizzbuzz.txt",
            log_file,
        )
        log_print("Please create this file with your OpenRouter API key.", log_file)
        log_file.close()
        return

    score = run_fizzbuzz_game(
        api_key=api_key,
        log_file=log_file,
        model_name=args.model,
        fizz_num=args.fizz_num,
        buzz_num=args.buzz_num,
        max_turns=args.max_turns,
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
