"""
Fizzbuzz Benchmark for LLMs - Anthropic Claude API
Uses the Anthropic Messages API (client.messages.create)
"""

import argparse
import os
from anthropic import Anthropic

# import ipdb
from utils import log_print, get_fizzbuzz_response


def run_fizzbuzz_game(
    client,
    log_file,
    model_name: str,
    fizz_num: int = 3,
    buzz_num: int = 5,
    max_turns: int = 100,
) -> int:
    """
    Run a Fizzbuzz game with an LLM and return the turn number where it failed.
    Returns 0 if it fails on the first turn, or the turn number of the last correct answer.
    """
    log_print(f"Testing {model_name}", log_file)

    with open("SYSTEM_PROMPT.md", "r") as f:
        system_prompt = f.read().strip().format(fizz_num=fizz_num, buzz_num=buzz_num)

    messages = [{"role": "user", "content": "1"}]
    log_print("Turn 1: User said 1", log_file)

    turn = 2  # LLM should respond with turn 2

    while True:
        try:
            response = client.messages.create(
                model=model_name,
                messages=messages,
                system=system_prompt,
                max_tokens=1256,
                # thinking={"type": "enabled", "budget_tokens": 1024}, # use for claude 3.5 and older models
                thinking={"type": "adaptive"},
                output_config={"effort": "high"},
            )
            # ipdb.set_trace()
            llm_response = response.content[-1].text

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

            messages.append({"role": "assistant", "content": response.content})

            turn += 1
            user_response = get_fizzbuzz_response(turn, fizz_num, buzz_num)
            messages.append({"role": "user", "content": user_response})

            log_print(f"Turn {turn}: User said '{user_response}'", log_file)

            turn += 1

            if turn > max_turns:
                return max_turns

        except Exception as e:
            log_print(f"ERROR at turn {turn}: {e}", log_file)
            return turn - 1


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark LLMs on FizzBuzz using Anthropic Messages API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fizzbuzz_anthropic.py --model claude-sonnet-4-5-20250929
  python fizzbuzz_anthropic.py --model claude-opus-4-5-20251101 --fizz 2 --buzz 7
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
        default="claude-sonnet-4-5-20250929",
        help="Model to use (default: claude-sonnet-4-5-20250929)",
    )

    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)

    log_filename = f"logs/{args.model.replace('/', '_')}_fizz_{args.fizz_num}_buzz_{args.buzz_num}.log"
    log_file = open(log_filename, "w")

    log_print("Fizzbuzz LLM Benchmark - Anthropic Messages API", log_file)
    log_print("=" * 60, log_file)
    log_print(f"Game Rules: fizz={args.fizz_num}, buzz={args.buzz_num}", log_file)
    log_print("=" * 60, log_file)

    with open("../../Research/anthropic.txt", "r") as f:
        api_key = f.read().strip()
    client = Anthropic(api_key=api_key)

    score = run_fizzbuzz_game(
        client=client,
        log_file=log_file,
        model_name=args.model,
        fizz_num=args.fizz_num,
        buzz_num=args.buzz_num,
        max_turns=args.max_turns,
    )

    log_print(f"\n{'=' * 60}", log_file)
    log_print("FINAL RESULTS", log_file)
    log_print(f"Game Rules: fizz={args.fizz_num}, buzz={args.buzz_num}", log_file)
    log_print("=" * 60, log_file)
    log_print(f"{args.model}: {score} correct turns", log_file)
    log_print("=" * 60, log_file)

    log_file.close()


if __name__ == "__main__":
    main()
