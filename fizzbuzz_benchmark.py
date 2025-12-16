"""
Fizzbuzz Benchmark for LLMs
Tests OpenAI, Anthropic, and Together AI APIs on the classic Fizzbuzz game.
"""

import argparse
import os
from openai import OpenAI
from anthropic import Anthropic
from together import Together
import ipdb

# Global log file handle
_log_file = None

def log_print(message):
    """Print to console and log file simultaneously."""
    print(message)
    if _log_file:
        _log_file.write(message + '\n')
        _log_file.flush()

def get_fizzbuzz_response(number: int, fizz_num: int = 3, buzz_num: int = 5) -> str:
    """
    Returns the correct Fizzbuzz response for a given number.

    Args:
        number: The current turn number
        fizz_num: The number to check for "fizz" (default: 3)
        buzz_num: The number to check for "buzz" (default: 5)

    Rules:
    - Divisible by both fizz_num and buzz_num: "fizzbuzz"
    - Divisible by fizz_num: "fizz"
    - Divisible by buzz_num: "buzz"
    - Otherwise: the number itself as a string
    """
    if number % fizz_num == 0 and number % buzz_num == 0:
        return "fizzbuzz"
    elif number % fizz_num == 0:
        return "fizz"
    elif number % buzz_num == 0:
        return "buzz"
    else:
        return str(number)


def run_fizzbuzz_game(client, model_name: str, fizz_num: int = 3, buzz_num: int = 5, local:bool = False) -> int:
    """
    Run a Fizzbuzz game with an LLM and return the turn number where it failed.
    Returns 0 if it fails on the first turn, or the turn number of the last correct answer.

    Args:
        client: LLM API client
        model_name: Name of the API being tested
        fizz_num: The number to check for "fizz" (default: 3)
        buzz_num: The number to check for "buzz" (default: 5)
    """
    log_print(f"Testing {model_name}")

    # Initial system message and first user turn
    system_prompt = f"""You are playing FizzBuzz with the following rules:
    - If a number is divisible by {fizz_num}, say 'fizz'
    - If a number is divisible by {buzz_num}, say 'buzz'  
    - If a number is divisible by both {fizz_num} and {buzz_num}, say 'fizzbuzz'
    - Otherwise, say the number itself
    
    I will give you a number, and you must respond with the NEXT number (or word) in the sequence following these rules. Respond with ONLY the answer - just the number, 'fizz', 'buzz', or 'fizzbuzz'. No explanations, no additional text, no punctuation."""
    
    if model_name.startswith('claude'):
        # Anthropic messages API doesn't allow system role
        messages = [
            {
                "role": "user",
                "content": "1"
            }
        ]
    else:
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": "1"
            }
        ]

    turn = 2  # LLM should respond with turn 2

    while True:
        try:
            if model_name.startswith('gpt') or local:
                # OpenAI API
                response = client.responses.create(
                    model=model_name,
                    input=messages,
                    temperature=0,
                    max_output_tokens=16
                )
                llm_response = response.output[0].content[0].text
            
            elif model_name.startswith('claude'):
                # Anthropic API
                response = client.messages.create(
                    model=model_name,
                    messages=messages,
                    system=system_prompt,
                    temperature=0,
                    max_tokens=16
                )
                llm_response = response.content[0].text
            else:
                # Together API. Only difference from openai is max_tokens param name
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0,
                    max_tokens=16
                )
                llm_response = response.choices[0].message.content
            
            expected = get_fizzbuzz_response(turn, fizz_num, buzz_num)

            log_print(f"Turn {turn}: LLM said '{llm_response}' (expected '{expected}')")

            # Normalize responses for comparison (case-insensitive)
            llm_normalized = llm_response.lower().strip()
            expected_normalized = expected.lower().strip()

            # Check if response is correct
            if llm_normalized != expected_normalized:
                log_print(f"FAILED at turn {turn}!")
                log_print(f"Expected: {expected}")
                log_print(f" Got: {llm_response}")
                return turn - 1  # Return the last correct turn

            # Add LLM response to messages
            messages.append({
                "role": "assistant",
                "content": llm_response
            })

            # Prepare next user turn
            turn += 1
            user_response = get_fizzbuzz_response(turn, fizz_num, buzz_num)
            messages.append({
                "role": "user",
                "content": user_response
            })

            log_print(f"Turn {turn}: User said '{user_response}'")

            # Move to next LLM turn
            turn += 1
            
            if turn>100:
                return 100

        except Exception as e:
            log_print(f"ERROR at turn {turn}: {e}")
            return turn - 1


def main():
    global _log_file

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Benchmark LLMs on the Fizzbuzz game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fizzbuzz_benchmark.py                    # Classic Fizzbuzz (3 and 5)
  python fizzbuzz_benchmark.py --fizz 2 --buzz 7  # Custom numbers (2 and 7)
        """
    )
    parser.add_argument(
        "--fizz",
        type=int,
        default=3,
        dest="fizz_num",
        help="Number for 'fizz' (default: 3)"
    )
    parser.add_argument(
        "--buzz",
        type=int,
        default=5,
        dest="buzz_num",
        help="Number for 'buzz' (default: 5)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-5.2",
        help="Model to use. "
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Run inference on a local model served using vLLM"
    )

    args = parser.parse_args()

    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)

    # Open log file for this model
    log_filename = f"logs/{args.model.replace('/', '_')}" + f"_fizz_{args.fizz_num}_buzz_{args.buzz_num}" + ".log"
    _log_file = open(log_filename, 'w')

    log_print("Fizzbuzz LLM Benchmark")
    log_print("=" * 60)
    log_print(f"Game Rules: fizz={args.fizz_num}, buzz={args.buzz_num}")
    log_print("=" * 60)
    
    if args.model.startswith('gpt'):
        # Initialize OpenAI client
        with open('../../Research/openai.txt', 'r') as f:
            api_key = f.read().strip()
        client = OpenAI(api_key=api_key)
    elif args.local:
        client = OpenAI( 
            base_url="http://localhost:8000/v1",
            api_key="abc123",
            )
    elif args.model.startswith('claude'):
        # Initialize Anthropic client
        with open('../../Research/anthropic.txt', 'r') as f:
            api_key = f.read().strip()
        client = Anthropic(api_key=api_key)
    else:
        # Initialize Together client
        with open('../../Research/together.txt', 'r') as f:
            api_key = f.read().strip()
        client = Together(api_key=api_key)
        
    score = run_fizzbuzz_game(
        client,
        args.model,
        args.fizz_num,
        args.buzz_num,
        args.local
    )

    # Print final results
    log_print(f"\n{'='*60}")
    log_print("FINAL RESULTS")
    log_print(f"Game Rules: fizz={args.fizz_num}, buzz={args.buzz_num}")
    log_print('='*60)
    log_print(f"{args.model}: {score} correct turns")
    log_print('='*60)

    # Close log file
    if _log_file:
        _log_file.close()

    with open('RESULTS.log', 'a') as f:
        f.write(f"{args.model}: {score} correct turns for fizz:{args.fizz_num} and buzz: {args.buzz_num}\n")

if __name__ == "__main__":
    main()
