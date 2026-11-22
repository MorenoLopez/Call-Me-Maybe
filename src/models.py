#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   models.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: horarivo <horarivo@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/10/20 11:49:44 by horarivo            #+#    #+#            #
#   Updated: 2026/11/22 07:31:15 by horarivo           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from pydantic import BaseModel, ConfigDict
from typing import Literal


JsonType = Literal["boolean", "number", "string", "integer"]


class Parameter(BaseModel):
    """function parameter"""
    model_config = ConfigDict(extra="forbid")
    type: JsonType


class ReturnType(BaseModel):
    """Return type"""
    model_config = ConfigDict(extra="forbid")
    type: JsonType


class FunctionDefinition(BaseModel):
    """Function Definition"""
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str
    parameters: dict[str, Parameter]
    returns: ReturnType


class Prompt(BaseModel):
    """Prompt Entry"""
    model_config = ConfigDict(extra="forbid")
    prompt: str


class Output(BaseModel):
    """Output Entry"""
    prompt: str
    name: str
    parameters: dict[str, int | float | str | bool]
