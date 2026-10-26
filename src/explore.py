############
#          #
#   TEST   #
#          #
############

import time

from llm_sdk import Small_LLM_Model
from vocab import Vocab

model = Small_LLM_Model()

start = time.time()
vocab = Vocab.build(model)
print(f"built in {time.time() - start:.1f}s, {len(vocab.id_to_text)} usable")

sentence = "Hello é\nworld 42"
ids = model.encode(sentence).squeeze(0).tolist()
rebuilt = "".join(vocab.text_of(i) for i in ids)
print(repr(rebuilt), rebuilt == sentence)

logits = model.get_logits_from_input_ids(ids)
print("logits:", len(logits), "max id:", max(vocab.id_to_text))