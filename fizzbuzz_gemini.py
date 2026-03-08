"""
Fizzbuzz Benchmark for LLMs - Google Gemini API
Uses the new unified Google GenAI SDK (google-genai)
"""

import argparse
import os
from google import genai
from google.genai import types
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

    system_instruction = f"""You are playing FizzBuzz with the following rules:
    - If a number is divisible by {fizz_num}, say 'fizz'
    - If a number is divisible by {buzz_num}, say 'buzz'
    - If a number is divisible by both {fizz_num} and {buzz_num}, say 'fizzbuzz'
    - Otherwise, say the number itself

    I will give you a number, and you must respond with the NEXT number (or word) in the sequence following these rules. Respond with ONLY the answer - just the number, 'fizz', 'buzz', or 'fizzbuzz'. No explanations, no additional text, no punctuation."""

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        thinking_config=types.ThinkingConfig(
            thinking_level="high"
        ),  # for gemini3 and later
        # thinking_config=types.ThinkingConfig(thinkingBudget = -1) # for gemini2.5
    )

    chat = client.chats.create(model=model_name, config=config)

    log_print("Turn 1: User said 1", log_file)
    turn = 2  # LLM should respond with turn 2

    # Send first user message
    user_message = "1"

    while True:
        try:
            response = chat.send_message(user_message)
            llm_response = response.text
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
        description="Benchmark LLMs on FizzBuzz using Google Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fizzbuzz_gemini.py --model gemini-2.5-flash
  python fizzbuzz_gemini.py --model gemini-2.5-pro --fizz 2 --buzz 7
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
        default="gemini-2.5-flash",
        help="Model to use (default: gemini-2.5-flash)",
    )

    args = parser.parse_args()

    os.makedirs("logs", exist_ok=True)

    log_filename = f"logs/{args.model.replace('/', '_')}_fizz_{args.fizz_num}_buzz_{args.buzz_num}.log"
    log_file = open(log_filename, "w")

    log_print("Fizzbuzz LLM Benchmark - Google Gemini API", log_file)
    log_print("=" * 60, log_file)
    log_print(f"Game Rules: fizz={args.fizz_num}, buzz={args.buzz_num}", log_file)
    log_print("=" * 60, log_file)

    with open("../../Research/gemini.txt", "r") as f:
        api_key = f.read().strip()
    client = genai.Client(api_key=api_key)

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
