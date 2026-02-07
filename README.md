# Fizzbuzz LLM Benchmark

A (silly) benchmark for testing how well LLMs can play the children's game [Fizzbuzz](https://en.wikipedia.org/wiki/Fizz_buzz). I got the idea while writing [this blog post](https://venkatasg.net/blog/fizzbuzz-2025-12-11.html) and figured it would be a fun exercise. By customizing the `fizz` and `buzz` numbers, we can also test whether LLMs generalize to play the game by the new rules, or just memorize what they've seen about FizzBuzz from training.

**Does this say anything about the models?** Clearly this isn't reflective of any real-world tasks or uses for LLMs. But whether LLMs are good at [arithmetic and counting](https://loeber.substack.com/p/21-everything-we-know-about-llms), [long multi-turn conversations](https://openreview.net/forum?id=VKGTGGcwl6), and [generalization](https://aclanthology.org/2025.cxgsnlp-1.7/) are all active areas of research. This simple benchmark does test the model's ability at all 3!

My biggest takeaway is that (most) LLMs don't generalize to play the game of FizzBuzz with slightly different rules at all. But something changed with Gemini 3, GPT 5.2 and Claude 4.5, [which is consistent what others have been saying](https://simonwillison.net/2026/Jan/4/inflection/)&mdash;they all ace the task. I might have to run the benchmark for more turns🫠.

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

I report the number of turns until the model returned the wrong answer for its turn. I didn't check more than 200 turns because I don't want to spend too much money on this!

### GPT Models

| Model | Standard FizzBuzz | Buzz=7|
|-------|--------------------------|---------------|
| `gpt-5.2-pro` | **200** | **200** |
| `gpt-5.2` | 5 | 11 |
| `gpt-5.1` | 39 | 27 |
| `gpt-4.1` | 23 | 5 |
|` gpt-4.1-mini` | 33 | 5 |
| `gpt-4.1-nano` | 3 | 3 |
| `gpt-3.5-turbo` | 11 | 1 |

I'm not sure why GPT-5.2 fails so badly at the standard game of FizzBuzz?

### Claude (🏆) Models

| Model | Standard FizzBuzz | Buzz=7|
|-------|--------------------------|---------------|
| `claude-opus-4-6` | **200** | **181** |
| `claude-opus-4-5-20251101` | **200** | **181** |
| `claude-sonnet-4-5-20250929` | **200** | **200** |
| `claude-haiku-4-5-20251001` | 5 | 13 |
| `claude-sonnet-4-20250514` | **200** | **200** |
| `claude-3-7-sonnet-20250219` | *200* | 5 |

### Google Models

| Model | Standard FizzBuzz | Buzz=7|
|-------|--------------------------|---------------|
| `gemini-3-pro-preview` | 200 | 103 |
| `gemini-3-flash-preview` | 115 | 83 |
| `gemini-2.5-pro` | **200** | **200** |
| `gemini-2.5-flash` | 3 | 5 |
| `gemini-2.0-flash` | **200** | 39 |
| `google/gemma-3-27b-it` | 5 | 5 |

### Other Models

| Model | Standard FizzBuzz | Buzz=7|
|-------|--------------------------|---------------|
| `moonshotai/Kimi-K2-Thinking` | 21 | 9 |
| `moonshotai/Kimi-K2-Instruct-0905` | **200** | 19 |
| `zai-org/GLM-4.7` | 13 | 52 |
| `deepseek-ai/DeepSeek-V3-0324` | 43 | 9 |
| `deepseek-ai/DeepSeek-V3.1` | 95 | 5 |
| `meta-llama/Llama-3.3-70B-Instruct-Turbo` | 3 | 3 |
| `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | 5 | 41 |
| `Qwen/Qwen3-235B-A22B-Instruct-2507-tput` | 25 | 11 |
| `Qwen/Qwen3-Next-80B-A3B-Instruct` | 17 | 5 |

I'll add more models soon.

## Takeaways

- I noticed a lot of sensitivity to the system prompt. During preliminary testing, GPT-5.2 managed to go all the way to 2000(!) on standard FizzBuzz. I slightly modified the prompt since that run and can't replicate it anymore. 
- Some of the results make little sense to me. Why is `gemini-2.0-flash` better than `gemini-2.5-flash`? 🤷🏾‍♂️. I think there is too much randomness between runs, and the models are behind opaque APIs so its impossible to say anything for certain with the closed models (which are also, sadly, the best performing ones right now).
- ~~I set temperature to 0 (when possible) and left all other settings as is (thinking tokens/budget was set to around 128 when possible to save on costs). ~~I've left all parameters in their defaults because I realized this was disadvantaging a lot of models (especially with thinking). I don't specify any additional parameters for the model. This also tests the models ability to follow instructions (it should only output the next number after thinking how much ever it wants).

