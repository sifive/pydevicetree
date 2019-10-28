#!/usr/bin/env python3

from pyparsing import Word, Literal, nestedExpr, OneOrMore, delimitedList, Optional
from pyparsing import alphanums, hexnums, nums, printables

label = Word(alphanums + "_")
label_reference = Literal("&") + label
node_name = Word(alphanums + ",._+-")
unit_address = Word(hexnums)

property_name = Word(alphanums + ",._+?#")

decimal_int = Word(nums)
hexadecimal_int = Literal("0x") + Word(hexnums)

property_value_int = decimal_int ^ hexadecimal_int

unary_operator = Literal("!") ^ Literal("~")
unary_expr = unary_operator + property_value_int
binary_operator = Word("+-*/&|^<>", exact=1) ^ Literal("<<") ^ Literal(">>") ^ Literal("&&") ^ Literal("||") ^ Literal("<=") ^ Literal(">=") ^ Literal("==") ^ Literal("!=")
binary_expr = property_value_int + binary_operator + property_value_int
unit_arithmetic_expr = unary_expr ^ binary_expr ^ property_value_int

arithmetic_expr = nestedExpr(Literal("("), Literal(")"), content=unit_arithmetic_expr)

property_value_int_array = OneOrMore(arithmetic_expr)
property_value_string = Literal("\"") + Word(printables) + Literal("\"")
property_value_stringlist = delimitedList(property_value_string)

property_value = (Literal("<") + property_value_int_array + Literal(">")) ^ property_value_string ^ property_value_stringlist

property_definition = Optional(label + Literal(":")) + property_name + Literal("=") + property_value + Literal(";")

node_opener = Optional(label + Literal(":")) + node_name + Optional(Literal("@") + unit_address) + Literal("{")
node_closer = Literal("};")
node_definition = nestedExpr(node_opener, node_closer, content=property_definition)

dts_v1 = Literal("/dts-v1/;") + Literal("/") + Literal("{") + ZeroOrMore(property_definition ^ node_definition) + node_closer
