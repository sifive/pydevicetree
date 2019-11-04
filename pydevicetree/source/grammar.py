#!/usr/bin/env python3

import pyparsing as p # type: ignore

p.ParserElement.enablePackrat()

node_name = p.Word(p.alphanums + ",.-+_") ^ p.Literal("/")
integer = p.pyparsing_common.integer ^ (p.Literal("0x").suppress() + p.pyparsing_common.hex_integer)
unit_address = p.pyparsing_common.hex_integer
property_name = p.Word(p.alphanums + ",.-_+?#")
label = p.Word(p.alphanums + "_").setResultsName("label")
label_creation = p.Combine(label + p.Literal(":"))
string = p.QuotedString(quoteChar='"')
stringlist = p.delimitedList(string)
node_path = p.Combine(p.Literal("/") + p.delimitedList(node_name, delim="/") + p.Optional(p.Literal("@") + unit_address))
reference = p.Combine(p.Literal("&") + ((p.Literal("{") + node_path("path") + p.Literal("}")) ^ label))
directive = p.QuotedString(quoteChar="/", unquoteResults=False).setResultsName("directive") + p.Optional(string ^ property_name ^ node_name ^ reference ^ (integer * 2)).setResultsName("option") + p.Literal(";").suppress()

operator = p.oneOf("~ ! * / + - << >> < <= > >= == != & ^ | && ||")
arith_expr = p.Forward()
ternary_element = arith_expr ^ integer
ternary_expr = ternary_element + p.Literal("?") + ternary_element + p.Literal(":") + ternary_element
arith_expr = p.nestedExpr(content=(p.OneOrMore(operator ^ integer) ^ ternary_expr))

cell_array = p.Literal("<").suppress() + p.ZeroOrMore(integer ^ arith_expr ^ string ^ reference ^ label_creation) + p.Literal(">").suppress()
bytestring = p.Literal("[").suppress() + (p.OneOrMore(p.Word(p.hexnums, exact=2) ^ label_creation)) + p.Literal("]").suppress()
property_assignment = property_name("property_name") + p.Optional(p.Literal("=").suppress() + (cell_array ^ bytestring ^ stringlist)).setResultsName("value") + p.Literal(";").suppress()

node_opener = p.Optional(label_creation) + node_name("node_name") + p.Optional(p.Literal("@").suppress() + unit_address("address")) + p.Literal("{").suppress()
node_closer = p.Literal("}").suppress() + p.Literal(";").suppress()
node_definition = p.Forward()
node_definition << node_opener + p.ZeroOrMore(property_assignment ^ directive ^ node_definition) + node_closer

devicetree = p.ZeroOrMore(directive ^ node_definition)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        devicetree.parseFile(sys.argv[1]).pprint()
