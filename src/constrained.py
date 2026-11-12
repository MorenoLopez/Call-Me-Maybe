#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   constrained.py                                       :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: horarivo <horarivo@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/31 18:29:49 by horarivo            #+#    #+#            #
#   Updated: 2026/11/11 15:49:57 by horarivo           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


"""Constrained decoding: function choice and parameter generation."""

import json
import re
from collections.abc import Iterable
from typing import Any

from pydantic import BaseModel

from llm_sdk import Small_LLM_Model

from .models import FunctionDefinition, Output
from .vocab import Vocab

NUMBER_CHARS = set("0123456789.-")
CLOSER_TAIL = set(",}]: \n")
NUMBER_PARTIAL = re.compile(r"^-?(\d+\.?\d*)?$")
NUMBER_FULL = re.compile(r"^-?\d+(\.\d+)?$")
MAX_NUMBER_TOKENS = 20
MAX_STRING_TOKENS = 100


class TokenSets(BaseModel):
    """Token id sets computed once at startup from the vocabulary."""

    index: dict[str, list[int]]
    numeric: list[int]
    string_or_quote: list[int]
    quote: set[int]
    end: set[int]
    newline: set[int]

    @classmethod
    def build(cls, vocab: Vocab) -> "TokenSets":
        index: dict[str, list[int]] = {}
        numeric: list[int] = []
        string: list[int] = []
        quote: set[int] = set()
        end: set[int] = set()
        newline: set[int] = set()
        for token_id, text in vocab.id_to_text.items():
            if not text:
                continue
            index.setdefault(text, []).append(token_id)
            if set(text) <= NUMBER_CHARS:
                numeric.append(token_id)
            if text[0] == '"':
                if set(text[1:]) <= CLOSER_TAIL:
                    quote.add(token_id)
            elif '"' not in text and not any(
                ord(c) < 32 or ord(c) == 127 for c in text
            ):
                string.append(token_id)
            if text[0] in ",}":
                end.add(token_id)
            if text[0] == "\n":
                newline.add(token_id)
        return cls(
            index=index,
            numeric=numeric,
            string_or_quote=string + list(quote),
            quote=quote,
            end=end,
            newline=newline,
        )


# def build_context(functions: list[FunctionDefinition], prompt: str) -> str:
#     """Build the text given to the model before the answer."""
#     system = [
#         "Choose the function that best answers the user request.",
#         "",
#         "Available functions:",
#     ]
#     for f in functions:
#         params = ", ".join(f"{n}: {p.type}" for n, p in f.parameters.items())
#         system.append(f"- {f.name}({params}): {f.description}")
#     system += ["", f"User request: {prompt}", "", "Function to call:", ""]
#     return "\n".join(system)

def build_context(functions: list[FunctionDefinition], prompt: str) -> str:
    """Build the ChatML-formatted prompt."""
    system = (
        "Choose the function that best answers "
        "the user request.\n\n"
        "Available functions:\n"
    )
    for f in functions:
        params = ", ".join(f"{n}: {p.type}" for n, p in f.parameters.items())
        system += f"- {f.name}({params}): {f.description}\n"

    # Format ChatML de Qwen3
    return (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\nUser request: {prompt}<|im_end|>\n"
        f"<|im_start|>assistant\n<think>\n\n</think>\n\n"
    )


def append_text(
    model: Small_LLM_Model, context_ids: list[int], text: str
) -> None:
    """Add skeleton text (written by us, not the model) to the context."""
    if text:
        context_ids.extend(model.encode(text).squeeze(0).tolist())


def pick_best(logits: list[float], allowed: Iterable[int]) -> int:
    """Return the allowed id with the highest logit."""
    return max(allowed, key=logits.__getitem__)


def choose_from_list(
    model: Small_LLM_Model,
    vocab: Vocab,
    tokens: TokenSets,
    options: list[str],
    context_ids: list[int],
) -> str:
    """Let the model pick one of the options, token by token."""
    so_far = ""
    while True:
        extendable = [o for o in options if o != so_far
                      and o.startswith(so_far)]
        if so_far in options and not extendable:
            return so_far
        if so_far not in options and len(extendable) == 1:
            # only one candidate left: no choice, complete it ourselves
            append_text(model, context_ids, extendable[0][len(so_far):])
            return extendable[0]

        allowed: set[int] = set()
        for option in extendable:
            rest = option[len(so_far):]
            for k in range(1, len(rest) + 1):
                allowed.update(tokens.index.get(rest[:k], []))
        can_stop = so_far in options
        if can_stop:
            allowed.update(tokens.newline)
        if not allowed:
            raise ValueError(f"no valid token after {so_far!r}")

        logits = model.get_logits_from_input_ids(context_ids)
        best_id = pick_best(logits, allowed)
        if can_stop and best_id in tokens.newline:
            return so_far
        so_far += vocab.text_of(best_id)
        context_ids.append(best_id)


def choose_function(
    model: Small_LLM_Model,
    vocab: Vocab,
    tokens: TokenSets,
    functions: list[FunctionDefinition],
    prompt: str,
) -> tuple[str, list[int]]:
    """Return the chosen function name and the updated context ids."""
    if not functions:
        raise ValueError("No function available")
    text = build_context(functions, prompt)
    context_ids: list[int] = model.encode(text).squeeze(0).tolist()
    names = [f.name for f in functions]
    name = choose_from_list(model, vocab, tokens, names, context_ids)
    return name, context_ids


def generate_number(
    model: Small_LLM_Model,
    vocab: Vocab,
    tokens: TokenSets,
    context_ids: list[int],
) -> float:
    """Generate a number; the end token is not added to the context."""
    so_far = ""
    for _ in range(MAX_NUMBER_TOKENS):
        allowed = [
            i for i in tokens.numeric
            if NUMBER_PARTIAL.match(so_far + vocab.text_of(i))
        ]
        complete = NUMBER_FULL.match(so_far) is not None
        if complete:
            allowed.extend(tokens.end)
        if not allowed:
            raise ValueError(f"no valid token after number {so_far!r}")
        logits = model.get_logits_from_input_ids(context_ids)
        best_id = pick_best(logits, allowed)
        if complete and best_id in tokens.end:
            break
        so_far += vocab.text_of(best_id)
        context_ids.append(best_id)
    so_far = so_far.rstrip(".")
    if NUMBER_FULL.match(so_far) is None:
        raise ValueError(f"no valid number generated: {so_far!r}")
    return float(so_far)


def generate_string(
    model: Small_LLM_Model,
    vocab: Vocab,
    tokens: TokenSets,
    context_ids: list[int],
) -> str:
    """Generate a string; the closing quote is added to the context."""
    so_far = ""
    for _ in range(MAX_STRING_TOKENS):
        logits = model.get_logits_from_input_ids(context_ids)
        best_id = pick_best(logits, tokens.string_or_quote)
        if best_id in tokens.quote:
            break
        so_far += vocab.text_of(best_id)
        context_ids.append(best_id)
    append_text(model, context_ids, '"')
    return so_far


def generate_boolean(
    model: Small_LLM_Model,
    vocab: Vocab,
    tokens: TokenSets,
    context_ids: list[int],
) -> bool:
    """Generate true or false."""
    word = choose_from_list(
        model, vocab, tokens, ["true", "false"], context_ids
    )
    return word == "true"


def generate_parameters(
    model: Small_LLM_Model,
    vocab: Vocab,
    tokens: TokenSets,
    func: FunctionDefinition,
    context_ids: list[int],
) -> dict[str, Any]:
    """Generate the values of all parameters of func."""
    append_text(model, context_ids, "\nParameters: ")
    if not func.parameters:
        append_text(model, context_ids, "{}")
        return {}
    result: dict[str, Any] = {}
    for i, (pname, param) in enumerate(func.parameters.items()):
        prefix = ("{" if i == 0 else ", ") + json.dumps(pname) + ": "
        if param.type == "string":
            prefix += '"'
        append_text(model, context_ids, prefix)
        if param.type == "number":
            result[pname] = generate_number(model, vocab, tokens, context_ids)
        elif param.type == "string":
            result[pname] = generate_string(model, vocab, tokens, context_ids)
        else:
            result[pname] = generate_boolean(
                model, vocab, tokens, context_ids
            )
    append_text(model, context_ids, "}")
    return result


def process_prompt(
    model: Small_LLM_Model,
    vocab: Vocab,
    tokens: TokenSets,
    functions: list[FunctionDefinition],
    prompt: str,
) -> Output:
    """Turn one prompt into a function call."""
    name, context_ids = choose_function(
        model, vocab, tokens, functions, prompt
    )
    func = next(f for f in functions if f.name == name)
    params = generate_parameters(model, vocab, tokens, func, context_ids)
    return Output(prompt=prompt, name=name, parameters=params)
