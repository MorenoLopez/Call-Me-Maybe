*This project has been created as part of the 42 curriculum by <horarivo.*

# call me maybe

## Description

call me maybe is a function calling tool that translates natural language prompts into structured function calls using a small language model (Qwen/Qwen3-0.6B). Given a prompt like "What is the sum of 40 and 2?", the program produces a JSON object containing the function name and its arguments, rather than a plain text answer.

The core challenge is reliability: a 0.6B parameter model left to its own devices produces valid JSON only about 30% of the time. This project solves that with **constrained decoding**, a technique that guides the model token by token so that every output is 100% valid JSON that conforms to the expected schema.

## Instructions

### Requirements

- Python 3.10 or later
- [uv](https://docs.astral.sh/uv/) for dependency management

### Installation

Clone the repository, then run:

```bash
uv sync
```

This installs all dependencies, including `llm_sdk` from the local directory, `pydantic`, and `numpy`.

### Running the program

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

All three arguments are optional and default to the paths above.

### Makefile

```bash
make install   # install dependencies
make run       # run with default paths
make debug     # run with pdb debugger
make lint      # flake8 + mypy
make clean     # remove __pycache__, .mypy_cache
```

## Algorithm explanation

### Constrained decoding

Language models generate text one token at a time. At each step, the model produces a probability score (logit) for every token in its vocabulary (~150,000 tokens for Qwen3-0.6B). Normally, the highest-scoring token is chosen. Constrained decoding intervenes **before** that choice:

1. The model produces logits for all tokens.
2. We determine which tokens are valid at this point in the JSON structure and schema.
3. We set all other logits to `-inf`.
4. We pick the best token among the remaining valid ones.

This guarantees that every generated token is structurally and semantically valid, making the output 100% parseable JSON that matches the schema every time.

### Generation pipeline

For each prompt, the pipeline runs in two phases.

**Phase 1 — function selection**  
We build a context in ChatML format (the conversation format Qwen3 was trained on) containing the available functions and the user's prompt. We then generate the function name token by token, constraining the model at each step to only tokens that extend a valid function name from our list. When only one candidate remains, we complete the name without calling the model (a shortcut that saves a few inference calls).

**Phase 2 — parameter generation**  
Once the function is known, we know its parameter names and types from `functions_definition.json`. We write the JSON skeleton ourselves (`{"param_name": `) and let the model fill in only the values, constrained by type:

- **number**: only tokens made of digits, `.`, and `-`, such that the accumulated string remains a valid number prefix. Generation stops when the model picks a terminator token (`,` or `}`).
- **string**: all tokens without a double-quote or control character. Generation stops when the model picks a closing-quote token.
- **boolean**: constrained to `true` or `false` using the same mechanism as function selection.

### Vocabulary table

At startup we decode every token id once using `model.decode([id])` and store the result in a table (`id → text`). We also precompute sets of valid token ids for each type (numeric tokens, string-safe tokens, closing-quote tokens, end tokens). This avoids scanning 150,000 tokens at every generation step.

## Design decisions

- **pydantic for all models**: input files are validated against `FunctionDefinition`, `Prompt`, and `Output` models. Invalid entries are rejected with a clear error message.
- **ChatML format**: we use Qwen3's native conversation format, with thinking disabled (`<think>\n\n</think>`), so the model is in the state it was trained for.
- **Skeleton written by us, values by the model**: we never ask the model to produce `{`, `"`, `:`, or key names. This eliminates the main source of JSON errors in small models.
- **One model load per run**: `Small_LLM_Model`, `Vocab`, and `TokenSets` are built once before the prompt loop. Each prompt failure is caught individually, so one bad prompt does not stop the rest.
- **No private SDK attributes**: only the four public methods of `Small_LLM_Model` are used (`encode`, `decode`, `get_logits_from_input_ids`, `get_path_to_vocab_file`).

## Performance analysis

Measured on the provided 11-prompt test set:

| prompt type | time per prompt |
|---|---|
| simple (number, short string) | ~3–4 s |
| multi-parameter with regex | ~11–15 s |
| total (11 prompts) | ~59 s |

Each token generation requires one full forward pass of the model on the entire context. There is no KV cache available through the SDK, so longer contexts cost more. The 5-minute limit comfortably covers the provided test set; with larger sets or longer function lists, context length becomes the bottleneck.

**Known limitations**:
- Negative numbers in arguments may not be extracted correctly: the model tends to ignore the leading `-` sign.
- String values that should start with a space are generated without it.
- Multi-byte Unicode characters split across tokens (e.g. some emoji) cannot appear in generated strings.

## Challenges faced

- **`squeeze()` on a single-token encoding** returned a scalar instead of a list; fixed with `squeeze(0)`.
- **Local `llm_sdk` package not found** when declared as a PyPI dependency in `pyproject.toml`; fixed by declaring it as a local path dependency with `uv add ./llm_sdk`.
- **Relative imports** (`from .models import ...`) are required when running with `python -m src`; plain imports work only when running files directly.
- **Regex extraction**: with a plain-text context, the model copied a literal number from the prompt instead of inferring a regex pattern. Switching to ChatML format fixed this.

## Testing strategy

Manual testing against the provided 11-prompt set after each change, checking:
- correct function name for every prompt,
- correct argument types (number, string, boolean),
- JSON validity of the output file.

Edge cases tested: empty parameter list, negative numbers, floating-point numbers, strings with apostrophes, strings with regex special characters.

The output file is always valid JSON regardless of model quality, because the structure is enforced by constrained decoding, not by prompting.

## Example usage

Run with default paths:

```bash
uv run python -m src
```

Run with custom paths:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calls.json
```

Expected output format:

```json
[
    {
        "prompt": "What is the sum of 2 and 3?",
        "name": "fn_add_numbers",
        "parameters": {"a": 2.0, "b": 3.0}
    },
    {
        "prompt": "Greet john",
        "name": "fn_greet",
        "parameters": {"name": "john"}
    }
]
```

## Resources

- [Qwen3 model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Qwen3 technical report](https://arxiv.org/abs/2505.09388)
- [ChatML format documentation](https://huggingface.co/docs/transformers/chat_templating)
- [Constrained decoding — survey paper](https://arxiv.org/abs/2406.06608)
- [JSON grammar for constrained generation (Outlines)](https://github.com/outlines-dev/outlines)
- [BPE tokenization (original paper)](https://arxiv.org/abs/1508.07909)

### AI usage

AI was used throughout this project as a guided assistant:
- explaining the constrained decoding algorithm and the generation pipeline step by step,
- reviewing Python code for correctness (import errors, type annotations),
- debugging runtime errors (squeeze, relative imports, local package installation),
- improving README.