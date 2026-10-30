############
#          #
#   TEST   #
#          #
############

import time
from pathlib import Path

from llm_sdk import Small_LLM_Model
from constrained import build_text_index, choose_function
from utils import json_load, validate
from models import FunctionDefinition, Prompt
from vocab import Vocab

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

for p in prompts:
    start = time.time()
    name = choose_function(model, vocab, index, functions, p.prompt)
    print(f"{p.prompt!r} -> {name}  ({time.time() - start:.1f}s)")
