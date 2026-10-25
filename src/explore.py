import json

from llm_sdk import Small_LLM_Model

model = Small_LLM_Model()
path = model.get_path_to_vocab_file()
print("path:", path)

with open(path, "r", encoding="utf-8") as f:
    vocab = json.load(f)

print("type:", type(vocab))
print("size:", len(vocab))

if isinstance(vocab, dict):
    print("first 10:", list(vocab.items())[:10])
    for key in ["{", '"', "1", "Ġthe", " the"]:
        print(repr(key), "->", vocab.get(key))
else:
    print("first 10:", vocab[:10])
