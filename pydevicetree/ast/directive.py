#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

from typing import List, Any

from pydevicetree.ast.helpers import formatLevel

class Directive:
    def __init__(self, directive: str, options: List[Any] = None):
        """Create a directive object"""
        self.directive = directive
        self.options = options

    def __repr__(self) -> str:
        return "<Directive %s>" % self.directive

    def __str__(self) -> str:
        return self.to_dts()

    def to_dts(self, level: int = 0) -> str:
        """Format the Directive in Devicetree Source format"""
        if self.options:
            return formatLevel(level, "%s %s;\n" % (self.directive, self.options))
        return formatLevel(level, "%s;\n" % self.directive)
