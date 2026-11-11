#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: horarivo <horarivo@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/20 09:42:35 by horarivo            #+#    #+#            #
#   Updated: 2026/11/11 14:03:50 by horarivo           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Entry point of the function calling tool."""

import argparse
import json
import sys
import time
from pathlib import Path

from llm_sdk import Small_LLM_Model

from .constrained import TokenSets, process_prompt
from .models import FunctionDefinition, Output, Prompt
from .utils import json_load, validate
from .vocab import Vocab

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def get_args() -> argparse.Namespace:
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(
        prog="python -m src",
        description="Translate natural language prompts into function calls.",
    )
    parser.add_argument(
        "--functions_definition",
        type=Path,
        default=Path("data/input/functions_definition.json"),
        help="path to the functions definition file",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/input/function_calling_tests.json"),
        help="path to the prompts file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/output/function_calling_results.json"),
        help="path to the output file",
    )
    return parser.parse_args()


def write_results(path: Path, results: list[Output]) -> None:
    """Write the results as a JSON array, creating the folder if needed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(
                [r.model_dump() for r in results],
                file,
                indent=4,
                ensure_ascii=False,
            )
    except OSError as err:
        raise ValueError(f"cannot write {path}: {err}") from None


def print_result(i: int, total: int, out: Output) -> None:
    """Print one result as a colored JSON block."""
    block = json.dumps(out.model_dump(), indent=4, ensure_ascii=False)
    for key in ("prompt", "name", "parameters"):
        block = block.replace(f'"{key}"', f'{CYAN}"{key}"{RESET}')
    print(f"\n{YELLOW}[{i}/{total}]{RESET}")
    print(block)


def main() -> int:
    args = get_args()
    try:
        functions = validate(
            json_load(args.functions_definition), FunctionDefinition
        )
        prompts = validate(json_load(args.input), Prompt)
        if not functions:
            raise ValueError("no function in the definitions file")
        model = Small_LLM_Model()
        vocab = Vocab.build(model)
        tokens = TokenSets.build(vocab)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted.{RESET}", file=sys.stderr)
        return 130
    except Exception as err:
        print(f"{RED}[ Error]{RESET} : {err}", file=sys.stderr)
        return 1

    results: list[Output] = []
    start = time.time()
    try:
        for i, p in enumerate(prompts, 1):
            try:
                out = process_prompt(model, vocab, tokens, functions, p.prompt)
            except Exception as err:
                print(
                    f"{RED}[ Error]{RESET} prompt {i} skipped: {err}",
                    file=sys.stderr,
                )
                continue
            results.append(out)
            print_result(i, len(prompts), out)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted after {i - 1} prompt(s).{RESET}",
              file=sys.stderr)

    if not results:
        return 130

    try:
        write_results(args.output, results)
    except ValueError as err:
        print(f"{RED}[ Error]{RESET} : {err}", file=sys.stderr)
        return 1

    elapsed = time.time() - start
    status = GREEN if len(results) == len(prompts) else YELLOW
    print(
        f"\n{status}{len(results)}/{len(prompts)} prompts done "
        f"in {elapsed:.1f}s{RESET} -> {args.output}"
    )
    return 0 if len(results) == len(prompts) else 1


if __name__ == "__main__":
    sys.exit(main())
