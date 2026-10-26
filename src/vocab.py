#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   vocab.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: horarivo <horarivo@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/26 08:15:11 by horarivo            #+#    #+#            #
#   Updated: 2026/10/26 09:02:39 by horarivo           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


import json
from pathlib import Path
from pydantic import BaseModel
from llm_sdk import Small_LLM_Model


class Vocab(BaseModel):
    id_to_text: dict[int, str]

    @classmethod
    def build(cls, model: Small_LLM_Model) -> "Vocab":
        path = Path(model.get_path_to_vocab_file())
        try:
            with open(path, "r", encoding="utf-8") as file:
                raw = json.load(file)
        except OSError as err:
            raise ValueError(f"cannot read vocab file {path}: {err}") from None
        except json.JSONDecodeError as err:
            raise ValueError(f"invalid vocab file {path}: {err}") from None
        if not isinstance(raw, dict):
            raise ValueError(f"{path} must contain a JSON object")

        id_to_text: dict[int, str] = {}
        for token_id in raw.values():
            text = model.decode([token_id])
            if "\ufffd" in text:
                continue
            id_to_text[token_id] = text
        return cls(id_to_text=id_to_text)

    def text_of(self, token_id: int) -> str:
        return self.id_to_text[token_id]

    def is_usable(self, token_id: int) -> bool:
        return token_id in self.id_to_text
