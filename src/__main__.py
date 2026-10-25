#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   __main__.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: horarivo <horarivo@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/20 09:42:35 by horarivo            #+#    #+#            #
#   Updated: 2026/10/25 08:44:56 by horarivo           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""entry file"""

import argparse
import sys
from pathlib import Path
from .utils import json_load, validate
from .models import Prompt, FunctionDefinition

def get_args() -> argparse.Namespace:
    """Parse the command line arguments.

    Returns:
        The parsed arguments.
    """
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


def main() -> int:
    """Run the program

    Returns:
        The exit code (0 on success, 1 on error).
    """
    args = get_args()
    try:
        functions = validate(json_load(args.functions_definition), FunctionDefinition)
        prompts = validate(json_load(args.input), Prompt)
    except Exception as e:
        print(f"[ Error] : {e}", file=sys.stderr)
        return 1
    print("\n\n - [ Everything looks good ]")
    return 0

if __name__=="__main__":
    sys.exit(main())