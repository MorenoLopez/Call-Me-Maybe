#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   constrained.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: horarivo <horarivo@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/31 18:29:49 by horarivo            #+#    #+#            #
#   Updated: 2026/11/01 07:47:29 by horarivo           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


import numpy as np
from models import FunctionDefinition


def build_context(functions: list[FunctionDefinition], prompt: str) -> str:
    lines = [
        "Pick the function that best answers the user request.",
        "",
        "Available functions:",
    ]
    for f in functions:
        params = ", ".join(f"{n}: {p.type}" for n, p in f.parameters.items())
        lines.append(f"- {f.name}({params}): {f.description}")
    lines += ["", f"User request: {prompt}", "", "Function to call:", ""]
    print(f"""
        {params}
        {lines}
    """)
    return "\n".join(lines)

def build_text_index(vocab) -> dict[str, list[int]]:
    """ done ONCE at startup: token text -> all ids having that text """
    index = {}
    for token_id, text in vocab.id_to_text.items():
        index.setdefault(text, []).append(token_id)
    return index


def choose_function(model, vocab, index, functions, prompt) -> str:
    names = [f.name for f in functions]
    context_ids = model.encode(build_context(functions, prompt)).squeeze(0).tolist()
    gen_name = ""

    while True:
        if gen_name in names:
            return gen_name

        # what is still left to write, for each candidate name
        remainders = [name[len(gen_name):] for name in names if name.startswith(gen_name)]

        # tokens whose text is a non-empty beginning of a remainder
        allowed = set()
        for r in remainders:
            for k in range(1,len(r) + 1):
                allowed.update(index.get(r[:k], []))

        if not allowed:
            raise ValueError("No valid token to continue the function name")

        logits = model.get_logits_from_input_ids(context_ids)

        # masking: everything not allowed gets -inf
        masked = [float("-inf")] * len(logits)
        for token_id in allowed:
            masked[token_id] = logits[token_id]

        best_id = masked.index(max(masked))
        gen_name += vocab.text_of(best_id)
        context_ids.append(best_id)
