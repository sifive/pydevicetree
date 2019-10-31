#!/usr/bin/env python3

import unittest
import os
from source import *

devicetreedirs = ["tests/devicetrees/", "tests/devicetrees/sifive/"]

def compareIgnoreNewlines(a, b):
    import re
    whitespace = re.compile(r"^\s+$")
    def predicate(line):
        if whitespace.match(line) is not None:
            return False # skip
        if line == '':
            return False
        return True

    a = filter(predicate, a.split("\n"))
    b = filter(predicate, b.split("\n"))

    line = 0
    for x, y in zip(a, b):
        if x.strip() != y.strip():
            print("< %d" % line)
            print(x)
            print(">")
            print(y)
            return False
        line += 1

    return True

class TestDevicetreeSource(unittest.TestCase):
    #@unittest.skip
    def test_devicetree(self):
        devicetrees = []
        for d in devicetreedirs:
            for f in os.listdir(d):
                if f[-4:] == ".dts":
                    devicetrees.append(d + f)

        for i in devicetrees:
            with self.subTest(devicetree=i):
                print("Testing DTS %s" % i)
                with open(i, "r") as f:
                    contents = f.read()

                tree = parseTree(contents)
                backtosource = dumpDTS(tree)

                # DTS -> Tree -> DTS should yield identical Devicetree sources
                self.assertTrue(compareIgnoreNewlines(contents, backtosource))
                
                backtotree = parseTree(backtosource)
                backtosourceagain = dumpDTS(backtotree)

                # DTS -> Tree -> DTS -> Tree -> DTS should yield all identical
                # identical Devicetree Sources
                self.assertTrue(compareIgnoreNewlines(contents, backtosourceagain))
                self.assertTrue(compareIgnoreNewlines(backtosource, backtosourceagain))

if __name__ == "__main__":
    unittest.main()
