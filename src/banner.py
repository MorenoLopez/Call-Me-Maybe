#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   banner.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: horarivo <horarivo@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/11/17 08:51:52 by horarivo            #+#    #+#            #
#   Updated: 2026/11/22 07:31:14 by horarivo           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""ASCII art banner for the program."""

import shutil
from pathlib import Path


def print_banner(color: str = "", reset: str = "") -> None:
    """Print the banner split into chunks that fit the terminal width."""
    banner_path = Path(__file__).parent / "banner" / "banner.txt"
    try:
        lines = banner_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    if not any(line.strip() for line in lines):
        return
    width = shutil.get_terminal_size(fallback=(80, 24)).columns
    max_len = max((len(line) for line in lines), default=0)
    for start in range(0, max_len, width):
        for line in lines:
            chunk = line[start:start + width]
            if chunk.strip():
                print(color + chunk.center(width) + reset)
        if start + width < max_len:
            print()
