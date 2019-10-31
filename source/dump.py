#!/usr/bin/env python3

from ast.classes import *
from functools import reduce

def dumpDTS(tree, level=0):
    dts = ""

    def printlevel(level, s):
        return "\t" * level + s + "\n"

    def listIsAllStrings(l):
        def isString(e):
            return type(e) is str and e[0] != "&"

        return reduce(lambda b, e: b and isString(e), l, True)

    def formatList(l, formatHex=False):
        if listIsAllStrings(l):
            # Strings aren't contained by <>
            return ", ".join(["\"" + str(x) + "\"" for x in l])
        else:
            if formatHex:
                l = ["0x{:x}".format(x) for x in l if type(x) is int] + [str(x) for x in l if type(x) is not int]
                return "<" + " ".join(l) + ">"
            else:
                return "<" + " ".join([str(x) for x in l]) + ">"

    for item in tree:
        if type(item) is Node:
            if type(item.address) is int and item.label:
                dts += printlevel(level, "%s: %s@%x {" % (item.label, item.name, item.address))
            elif type(item.address) is int:
                dts += printlevel(level, "%s@%x {" % (item.name, item.address))
            elif item.label:
                dts += printlevel(level, "%s: %s {" % (item.label, item.name))
            else:
                dts += printlevel(level, "%s {" % item.name)

            dts += dumpDTS(item.properties, level=(level + 1))
            dts += dumpDTS(item.children, level=(level + 1))

            dts += printlevel(level, "};")

        elif type(item) is Property:
            if item.values:
                if item.name == "reg" or item.name == "ranges":
                    dts += printlevel(level, "%s = %s;" % (item.name, formatList(item.values, True)))
                else:
                    dts += printlevel(level, "%s = %s;" % (item.name, formatList(item.values)))
            else:
                dts += printlevel(level, "%s;" % item.name)

        elif type(item) is Directive:
            if item.options:
                dts += printlevel(level, "%s %s;" % (item.directive, item.options))
            else:
                dts += printlevel(level, "%s;" % item.directive)

    return dts

