############
#          #
#   TEST   #
#          #
############

import time
from pathlib import Path

from llm_sdk import Small_LLM_Model
from utils import json_load, validate
from models import FunctionDefinition, Prompt
from vocab import Vocab
from constrained import TokenSets, process_prompt

model = Small_LLM_Model()
vocab = Vocab.build(model)
index = build_text_index(vocab)

functions = validate(
    json_load(Path("data/input/functions_definition.json")),
    FunctionDefinition,
)
prompts = validate(
    json_load(Path("data/input/function_calling_tests.json")),
    Prompt,
)

tokens = TokenSets.build(vocab)
for p in prompts:
    start = time.time()
    out = process_prompt(model, vocab, tokens, functions, p.prompt)
    print(out.model_dump(), f"({time.time() - start:.1f}s)")
