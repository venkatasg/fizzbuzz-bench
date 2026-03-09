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
# Standard game for 100 turns
python fizzbuzz_anthropic.py

# Use 7 for fizz and 4 for buzz and play for 200 turns
python fizzbuzz_anthropic.py --fizz 7 --buzz 4 --turns 200
```

You can view the raw turn-based conversation for every model in the `logs/` folder.

## Leaderboard

| Model | Easy | Medium | Hard | Score |
|-------|--------------|------------|---------------|---------------|
| `gpt-5.2-pro` | 200 | 200 | 200 | 100.0 |
| `gpt-5.2`  | 92 | 133 | 119 | 59.2 |
| `gpt-5.1`| 117 | 129 | 147 | 67.3 |
| `gpt-5`| 200 | 73 | 77 | 50.1 |
| `gpt-5-mini`| 71 | 69 | 35 | 27.1 |
| `gpt-5-nano`| 8 | 35 | 21 | 11.7 |
| `gpt-4.1` | 200 | 5 | 7 | 22.4 |
|` gpt-4.1-mini` | 200 | 5 | 7 | 22.4 |
| `gpt-4.1-nano` | 3 | 5 | 3| 1.9 |
| `gpt-3.5-turbo` | 57 | 1 | 9 | 7.9 |
| `claude-opus-4-6` | 200 | 181 | 200 | 96.7 |
| `claude-sonnet-4-6` | 200 | 5 | 27 | 26.9 |
| `claude-opus-4-5` | 200 | 200 | 181 | 95.7 |
| `claude-sonnet-4-5` | 200 | 200 | 141 | 86.7 |
| `claude-haiku-4-5` | 5 | 13 | 5 | 3.9 |
| `claude-opus-4.1` | 200 | 57 | 200 | 75.0 |
| `claude-opus-4` | 200 | 200 | 181 | 95.7 |
| `claude-sonnet-4` | 200 | 200 | 141 | 86.7 |
| `gemini-3.1-pro-preview` | 200| 200 | 200 | 100.0 |
| `gemini-3.1-flash-lite` | 200 | 33 | 11 | 28.2 |
| `gemini-3-flash-preview` | 115 | 83 | 69 | 41.5 |
| `gemini-2.5-pro` | 200 | 200 | 113 | 80.4 |
| `gemini-2.5-flash` | 3 | 7 | 3 | 2.2 |
| `gemini-2.5-flash-lite` | 7 | 9 | 11 | 4.8 |
| `gemini-2.0-flash` | 200 | 39 | 29 | 33.4 |
| `GLM-5` | 61 | 29 | 9 | 13.2 |
<!-- | `Kimi-K2.5` | 13 | 5 |  |  | -->


## FAQs

**Does this say anything about the models?** Clearly this isn't reflective of any real-world tasks or uses for LLMs. But whether LLMs are good at [arithmetic and counting](https://loeber.substack.com/p/21-everything-we-know-about-llms), [long multi-turn conversations](https://openreview.net/forum?id=VKGTGGcwl6), and [generalization](https://aclanthology.org/2025.cxgsnlp-1.7/) are all active areas of research. This simple benchmark does test the model's ability at all 3!

**Why didn't you set temperature to zero/Are the results reproducible?**: I initially setup this benchmark to query all models with `temperature=0`. However, this lead to worse results on many models, and LLM providers even [advise against it for reasoning tasks](https://ai.google.dev/gemini-api/docs/text-generation#system-instructions). I've left all parameters in their defaults as I believe this gives models the biggest advantage (I set thinking as high as the API allows). As a result, the results are not (and cannot be) deterministic. I try to report the highest score I observe with a model when I run the benchmark. 

**Why haven't you gone beyond 200 turns/averaged over multiple restarts per model** There's only so much money I'm willing to burn on tokens for this benchmark 😅.