# Fizzbuzz LLM Benchmark

A silly benchmark for testing how well LLMs can play the children's game Fizzbuzz.

## How It Works

The benchmark tests LLMs on their ability to play Fizzbuzz correctly:

1. The user starts by saying "1" and instructs the LLM to respond with the next number
2. The game alternates between user and LLM turns
3. For each turn, the correct response is:
   - "fizz" if the number is divisible by `fizz_num` (default: 3)
   - "buzz" if the number is divisible by `buzz_num` (default: 5)
   - "fizzbuzz" if the number is divisible by both
   - The number itself otherwise
4. The game continues until the LLM makes a mistake
5. The benchmark tracks how many turns each LLM can correctly complete

The game can be generalized to use any two numbers for fizz and buzz, not just 3 and 5!

## Setup

## Usage

### Basic Usage (Classic Fizzbuzz with 3 and 5)

```bash
python fizzbuzz_benchmark.py
```

### Custom Numbers

You can customize which numbers trigger "fizz" and "buzz":

```bash
# Use 2 for fizz and 7 for buzz
python fizzbuzz_benchmark.py --fizz 2 --buzz 7

# Use 4 for fizz and 6 for buzz
python fizzbuzz_benchmark.py --fizz 4 --buzz 6
```

## Results



## Why This Benchmark?

Fizzbuzz is a simple pattern recognition game that tests:
- Following instructions precisely
- Maintaining context over multiple turns
- Applying simple mathematical rules consistently
- Responding with ONLY the required output (no additional explanation)

While silly, it's a fun way to test how well models can maintain simple rules across an extended conversation.
