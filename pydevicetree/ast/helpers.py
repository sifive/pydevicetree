#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Any

def formatLevel(level: int, s: str) -> str:
    return "\t" * level + s

def wrapStrings(values: List[Any], formatHex: bool = False) -> List[Any]:
    wrapped = []
    for v in values:
        if isinstance(v, str):
            if v[0] != '&':
                wrapped.append("\"%s\"" % v)
            else:
                wrapped.append(v)
        elif isinstance(v, int):
            if formatHex:
                wrapped.append("0x%x" % v)
            else:
                wrapped.append(str(v))
        else:
            wrapped.append(str(v))
    return wrapped
