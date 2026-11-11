#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   utils.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: horarivo <horarivo@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/20 15:58:49 by horarivo            #+#    #+#            #
#   Updated: 2026/11/11 14:16:00 by horarivo           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel


def json_load(path: Path) -> list[Any]:
    """Load JSON file"""
    try:
        with open(path, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise ValueError(f"file not found: {path}") from None
    except json.JSONDecodeError as err:
        raise ValueError(f"invalid JSON in {path}: {err}") from None
    except OSError as err:
        raise ValueError(f"cannot read {path}: {err}") from None
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def validate(data: list[Any], model: type[BaseModel]) -> list[Any]:
    """validate entry"""
    res = []
    for item in data:
        obj = model.model_validate(item)
        res.append(obj)
    return res
