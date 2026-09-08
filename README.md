# Fizzbuzz LLM Benchmark

A (silly) benchmark for testing how well LLMs can play the children's game [Fizzbuzz](https://en.wikipedia.org/wiki/Fizz_buzz). Models are given the following instructions:

```
You are playing FizzBuzz with the following rules:
- If a number is divisible by {fizz_num}, say 'fizz'
- If a number is divisible by {buzz_num}, say 'buzz'
- If a number is divisible by both {fizz_num} and {buzz_num}, say 'fizzbuzz'
- Otherwise, say the number itself

I will give you a number, and you must respond with the NEXT number (or word) in the sequence following these rules. Respond with ONLY the answer - just the number, 'fizz', 'buzz', or 'fizzbuzz'. No explanations, no additional text, no punctuation.
```

By customizing `fizz_num` and `buzz_num`, we can test whether LLMs generalize to play the game by the new rules, or just memorize what they've seen about FizzBuzz from training. The benchmark has 3 difficulty levels:

- *Easy*: standard FizzBuzz.
- *Medium*: `buzz_num` is 7.
- *Hard*: `fizz_num` is 7, `buzz_num` is 5.

The score at each level is normalized to 100, and a final composite score out of 100 is calculated to reward good generalization performance:

```
final_score = 0.2 * easy + 0.35 * medium + 0.45 * hard
```

## How to Run

Ensure you have API keys setup as environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc):

```bash
# Standard game for 200 turns
python fizzbuzz.py --model claude-sonnet-4-5-20250929 --reasoning

# Use 7 for fizz and 4 for buzz and play for 100 turns
python fizzbuzz.py --model gpt-4.1 --fizz 7 --buzz 4 --turns 100
```

### Local models

Pass a Chat Completions URL to `--model` and the benchmark plays against a
locally served model instead — vLLM, llama.cpp, LM Studio, Ollama, anything with
an OpenAI-compatible endpoint. No plugin and no API key needed; the endpoint is
asked which model it serves, and that name is what gets logged and scored:

```bash
# vLLM's default endpoint
python fizzbuzz.py --model http://localhost:8000/v1

# Ollama — the /v1 is optional, and '#' picks one when several are served
python fizzbuzz.py --model http://localhost:11434#qwen3:8b --fizz 7 --buzz 4
```

Set `LOCAL_API_KEY` if your server checks the `Authorization` header. Everything
else — `--fizz`, `--buzz`, `--turns`, `--reasoning`, the logs — works the same.

You can view the raw turn-based conversation for every model in the `logs/` folder.

## Leaderboard

You can view the leaderboard at [venkatasg.net/fizzbuzz-bench](https://venkatasg.net/fizzbuzz-bench/).


## FAQs

**Does this say anything about the models?** Clearly this isn't reflective of any real-world tasks or uses for LLMs. But whether LLMs are good at [arithmetic and counting](https://loeber.substack.com/p/21-everything-we-know-about-llms), [long multi-turn conversations](https://openreview.net/forum?id=VKGTGGcwl6), and [generalization](https://aclanthology.org/2025.cxgsnlp-1.7/) are all active areas of research. This simple benchmark does test the model's ability at all 3!

**Why didn't you set temperature to zero/Are the results reproducible?**: I initially setup this benchmark to query all models with `temperature=0`. However, this lead to worse results on many models, and LLM providers even [advise against it for reasoning tasks](https://ai.google.dev/gemini-api/docs/text-generation#system-instructions). I've left all parameters in their defaults as I believe this gives models the biggest advantage (I set thinking as high as the API allows). As a result, the results are not (and cannot be) deterministic. I try to report the highest score I observe with a model when I run the benchmark.

**Why haven't you gone beyond 200 turns/averaged over multiple restarts per model** There's only so much money I'm willing to burn on tokens for this benchmark 😅.