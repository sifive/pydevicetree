#!/usr/bin/env python3

from pyparsing import *

ParserElement.enablePackrat()

node_name = Word(alphanums + ",.-+_") ^ Literal("/")
integer = pyparsing_common.integer ^ (Literal("0x").suppress() + pyparsing_common.hex_integer)
unit_address = pyparsing_common.hex_integer
property_name = Word(alphanums + ",.-_+?#")
label = Word(alphanums + "_").setResultsName("label")
label_creation = Combine(label + Literal(":"))
string = QuotedString(quoteChar='"')
stringlist = delimitedList(string)
node_path = Combine(Literal("/") + delimitedList(node_name, delim="/") + Optional(Literal("@") + unit_address))
reference = Combine(Literal("&") + ((Literal("{") + node_path("path") + Literal("}")) ^ label))
directive = QuotedString(quoteChar="/", unquoteResults=False).setResultsName("directive") + Optional(property_name ^ node_name ^ reference ^ (integer * 2)).setResultsName("option") + Literal(";").suppress()

operands = [
        (oneOf("~ !"),   1, opAssoc.RIGHT),
        (oneOf("* /"),   2, opAssoc.LEFT),
        (oneOf("+ -"),   2, opAssoc.LEFT),
        (oneOf("<< >>"), 2, opAssoc.LEFT),
        (oneOf("< <="),  2, opAssoc.LEFT),
        (oneOf("> >="),  2, opAssoc.LEFT),
        (oneOf("== !="), 2, opAssoc.LEFT),
        (Literal("&"),   2, opAssoc.LEFT),
        (Literal("^"),   2, opAssoc.LEFT),
        (Literal("|"),   2, opAssoc.LEFT),
        (Literal("&&"),  2, opAssoc.LEFT),
        (Literal("||"),  2, opAssoc.LEFT),
        ((Literal("?"), Literal(":")), 3, opAssoc.RIGHT),
        ]
arith_expr = infixNotation(integer, operands)

array = Literal("<").suppress() + ZeroOrMore(arith_expr ^ string ^ reference ^ label_creation) + Literal(">").suppress()
bytestring = Literal("[") + (Word(hexnums) ^ label_creation) + Literal("]")
property_assignment = property_name("property_name") + Optional(Literal("=").suppress() + (array ^ bytestring ^ stringlist ^ label_creation)).setResultsName("value") + Literal(";").suppress()

node_opener = Optional(label_creation) + node_name("node_name") + Optional(Literal("@").suppress() + unit_address("address")) + Literal("{").suppress()
node_closer = Literal("}").suppress() + Literal(";").suppress()
node_definition = Forward()
node_definition << node_opener + ZeroOrMore(property_assignment ^ directive ^ node_definition) + node_closer

devicetree = ZeroOrMore(directive ^ node_definition)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        devicetree.parseFile(sys.argv[1]).pprint()
