#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   models.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: horarivo <horarivo@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/20 11:49:44 by horarivo            #+#    #+#            #
#   Updated: 2026/10/25 08:44:48 by horarivo           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from pydantic import BaseModel
from typing import Literal


JsonType = Literal["boolean", "number", "string"]


class Parameter(BaseModel):
    """function parameter"""
    type: JsonTypes


class ReturnType(BaseModel):
    """Return type"""
    type: JsonType


class FunctionDefinition(BaseModel):
    """Function Definition"""
    name: str
    description: str
    parameters: dict[str, Parameter]
    returns: ReturnType


class Prompt(BaseModel):
    """Prompt Entry"""
    prompt: str


class Output(BaseModel):
    """Output Entry"""
    prompt: str
    name: str
    parameters: dict[str, int | float | str | bool]