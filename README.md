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
- *Hard*: `fizz_num` is 7, `buzz_num` is 4.

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

#### Running open-weight models with llama.cpp

The open-weight results below were produced with a CUDA build of
[llama.cpp](https://github.com/ggml-org/llama.cpp) serving GGUF quantizations,
with the three difficulty levels running in parallel against one server:

```bash
llama-server -m Qwen3.8-27B-UD-Q8_K_XL.gguf --alias Qwen3.8-27B-UD-Q8_K_XL \
    --port 8081 --jinja --reasoning-format deepseek -np 3 -c 196608 -n -1 \
    --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0 \
    --chat-template-kwargs '{"preserve_thinking": false}'

python fizzbuzz.py --model http://127.0.0.1:8081/v1 --reasoning              # easy
python fizzbuzz.py --model http://127.0.0.1:8081/v1 --reasoning --buzz 7     # medium
python fizzbuzz.py --model http://127.0.0.1:8081/v1 --reasoning --fizz 7 --buzz 4  # hard
```

`--alias` sets the model name that ends up in the log filename. Sampling
parameters are the model card's recommended thinking-mode settings.

**Qwen3.8 needs `preserve_thinking: false`.** The `llm` library does not send a
model's previous `reasoning_content` back with the conversation, and Qwen3.8's
chat template (with its default `preserve_thinking: true`) then renders every
earlier assistant turn as an empty `<think></think>` block. The model imitates
that pattern and stops thinking after the first turn, scoring 3/9/27 instead of
69/45/83. Disabling `preserve_thinking` renders history as plain text, which is
also how hosted APIs behave. Qwen3.8's template also promotes
`reasoning_effort: high` to `xhigh`, so `--reasoning` already gives it the
maximum effort. Nemotron 3.5's template writes `<think></think>` into history by
design and keeps thinking, so it needs no extra flags.

Best observed scores for local runs (multiple attempts per level, same as the
hosted models; see the FAQ on reproducibility). Each model was run at two
precisions, and the score below is the best observed per level, with the
quantization that produced it in brackets:

| Model | Easy | Medium | Hard | Score |
|---|---|---|---|---|
| Qwen3.8-Flash-Next (125B-A6B) | 93 [Q8_0] | 93 [Q4_K_XL] | 147 [Q4_K_XL] | 58.7 |
| Qwen3.8-27B (dense) | 69 [Q8_K_XL] | 45 [Q8_K_XL] | 83 [Q8_K_XL] | 33.5 |
| Nemotron 3.5 Lightning (30B-A3B) | 39 [BF16] | 39 [BF16] | 39 [BF16] | 19.5 |

Quantizations are unsloth's for the Qwen models and ggml-org's for Nemotron.
Nemotron's three scores of 39 are a coincidence, not a bug: three different
mistakes that each happened to land on turn 40.

**Full precision is not worth the VRAM here.** Each model was also run at the
largest precision that fits on two 48 GB cards, and the result went in a
different direction for each one:

| Model | Precision | Size | Easy | Medium | Hard | Score |
|---|---|---|---|---|---|---|
| Qwen3.8-Flash-Next | UD-Q4_K_XL | 111 GB | 11 | 93 | 147 | 50.5 |
| Qwen3.8-Flash-Next | Q8_0 | 188 GB | 93 | 63 | 105 | 44.0 |
| Qwen3.8-27B | UD-Q8_K_XL | 31.5 GB | 69 | 45 | 83 | 33.5 |
| Qwen3.8-27B | BF16 (full) | 54.7 GB | 55 | 35 | 11 | 14.1 |
| Nemotron 3.5 Lightning | Q8_0 | 33.6 GB | 33 | 15 | 3 | 6.6 |
| Nemotron 3.5 Lightning | BF16 (full) | 63.2 GB | 39 | 39 | 39 | 19.5 |

Qwen3.8-27B scores worse at BF16, Nemotron scores better, and Flash-Next splits
(its Q8_0 is far better on easy and worse on the other two). The reason is that
run-to-run variance dwarfs any precision effect: across attempts with identical
weights, Qwen3.8-27B's Q8 hard score was 35, 67 and 83, Nemotron's BF16 medium
was 3, 3 and 39, and Flash-Next's Q8 easy was 5 and 93. At two or three attempts
per cell this benchmark cannot resolve a difference between quantizations.
Flash-Next has no full-precision row because its BF16 weights are ~250 GB.

Both Qwen models fail the *easy* level the same way — answering with the bare
number (`6`, `12`) where `fizz` or `buzz` is due — while playing the custom
rules far more carefully.

You can view the raw turn-based conversation for every model in the `logs/` folder.

## Leaderboard

You can view the leaderboard at [venkatasg.net/fizzbuzz-bench](https://venkatasg.net/fizzbuzz-bench/).


## FAQs

**Does this say anything about the models?** Clearly this isn't reflective of any real-world tasks or uses for LLMs. But whether LLMs are good at [arithmetic and counting](https://loeber.substack.com/p/21-everything-we-know-about-llms), [long multi-turn conversations](https://openreview.net/forum?id=VKGTGGcwl6), and [generalization](https://aclanthology.org/2025.cxgsnlp-1.7/) are all active areas of research. This simple benchmark does test the model's ability at all 3!

**Why didn't you set temperature to zero/Are the results reproducible?**: I initially setup this benchmark to query all models with `temperature=0`. However, this lead to worse results on many models, and LLM providers even [advise against it for reasoning tasks](https://ai.google.dev/gemini-api/docs/text-generation#system-instructions). I've left all parameters in their defaults as I believe this gives models the biggest advantage (I set thinking as high as the API allows). As a result, the results are not (and cannot be) deterministic. I try to report the highest score I observe with a model when I run the benchmark.

**Why haven't you gone beyond 200 turns/averaged over multiple restarts per model** There's only so much money I'm willing to burn on tokens for this benchmark 😅.