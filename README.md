# Fizzbuzz LLM Benchmark

A (silly) benchmark for testing how well LLMs can play the children's game [Fizzbuzz](https://en.wikipedia.org/wiki/Fizz_buzz). I got the idea while writing [this blog post](https://venkatasg.net/blog/fizzbuzz-2025-12-11.html) and figured it would be a fun exercise. By customizing the `fizz` and `buzz` numbers, we can also test whether LLMs generalize to play the game by the new rules, or just memorize what they've seen about FizzBuzz from training.

**Does this say anything about the models?** Clearly this isn't reflective of any real-world tasks or uses for LLMs. But whether LLMs are good at [arithmetic and counting](https://loeber.substack.com/p/21-everything-we-know-about-llms), [long multi-turn conversations](https://openreview.net/forum?id=VKGTGGcwl6), and [generalization](https://aclanthology.org/2025.cxgsnlp-1.7/) are all active areas of research. This simple benchmark does test the model's ability at all 3!

## How It Works

The benchmark tests LLMs on their ability to play Fizzbuzz correctly. This is the system prompt:

> You are playing FizzBuzz with the following rules:
> - If a number is divisible by {fizz_num}, say 'fizz'
> - If a number is divisible by {buzz_num}, say 'buzz'  
> - If a number is divisible by both {fizz_num} and {buzz_num}, say 'fizzbuzz'
> - Otherwise, say the number itself
> 
> I will give you a number, and you must respond with the NEXT number (or word) in the sequence following these rules. Respond with ONLY the answer - just the number, 'fizz', 'buzz', or 'fizzbuzz'. No explanations, no additional text, no punctuation.

I wanted to test the generalization abilities of LLMs at this simple turn-based game, so the `fizz` and `buzz` numbers are customizable.

```bash
# Standard game
python fizzbuzz_benchmark.py

# Use 2 for fizz and 7 for buzz
python fizzbuzz_benchmark.py --fizz 2 --buzz 7

# Use 3 for fizz and 7 for buzz
python fizzbuzz_benchmark.py --buzz 7
```

To test model generalization, I set `buzz` to 7 and left `fizz` as is. Initial results presented below are from API calls on December 13 2025. I used the official OpenAI and Anthropic API for their models, and used [together.ai](https://api.together.ai) for the rest since I have some unused API credits left on that service. You can view the raw turn-based conversation for every model in the `logs/` folder.

I used Claude Code to write the script and README.

## Results

I report the number of turns until the model returned the wrong answer for its turn. I didn't check 100 turns because I don't want to spend too much money on this!

### GPT Models

| Model | Standard FizzBuzz | Buzz=7|
|-------|--------------------------|---------------|
| `gpt-5.2-pro` | **100** | **100** |
| `gpt-5.2` | 5 | 11 |
| `gpt-5.1` | 39 | 27 |
| `gpt-4.1` | 100 | 5 |
|` gpt-4.1-mini` | 100 | 5 |
| `gpt-4.1-nano` | 3 | 3 |
| `gpt-3.5-turbo` | 63 | 5 |

I'm not sure why GPT-5.2 fails so badly at the standard game of FizzBuzz?

### Claude Models

| Model | Standard FizzBuzz | Buzz=7|
|-------|--------------------------|---------------|
| `claude-sonnet-4-5-20250929` | 100 | 41 |
| `claude-opus-4-5-20251101` | **100** | **100** |
| `claude-haiku-4-5-20251001` | 5 | 13 |
| `claude-sonnet-4-20250514` | **100** | **100** |
| `claude-3-7-sonnet-20250219` | 100 | 5 |

### Google Models

| Model | Standard FizzBuzz | Buzz=7|
|-------|--------------------------|---------------|
| `gemini-3-pro-preview` | 33 | 59 |
| `gemini-3-flash-preview` | 100 | 29 |
| `gemini-2.5-pro` | 100 | 7 |
| `gemini-2.5-flash` | 5 | 5 |
| `gemini-2.0-flash` | 100 | 49 |
| `google/gemma-3-27b-it` | 5 | 5 |

### Other Models

| Model | Standard FizzBuzz | Buzz=7|
|-------|--------------------------|---------------|
| `moonshotai/Kimi-K2-Thinking` | 27 | 23 |
| `moonshotai/Kimi-K2-Instruct-0905` | 100 | 3 |
| `zai-org/GLM-4.7` | 13 | 52 |
| `deepseek-ai/DeepSeek-V3-0324` | 43 | 9 |
| `deepseek-ai/DeepSeek-V3.1` | 100 | 5 |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo` | 3 | 3 |
| `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | 5 | 41 |
| `Qwen/Qwen3-235B-A22B-Instruct-2507-tput` | 25 | 11 |
| `Qwen/Qwen3-Next-80B-A3B-Instruct` | 17 | 5 |

I'll add more models soon.

## Takeaways

GPT-5.2, Claude Sonnet 4.5 and Opus 4.5 are the best, **but**:

- I noticed a lot of sensitivity to the system prompt. During preliminary testing, GPT-5.2 managed to go all the way to 2000(!) on standard FizzBuzz. I slightly modified the prompt since that run and can't replicate it anymore. 
- ~~I set temperature to 0 (when possible) and left all other settings as is (thinking tokens/budget was set to around 128 when possible to save on costs). ~~I've left all parameters in their defaults because I realized this was disadvantaging a lot of models (especially with thinking). I don't specify any additional parameters for the model. This also tests the models ability to follow instructions (it should only output the next number after thinking how much ever it wants).

My biggest takeaway is that LLMs don't generalize to play the game of FizzBuzz with slightly different rules at all.