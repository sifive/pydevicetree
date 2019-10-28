from pyparsing import *

node_name = Word(alphanums + ",.-+_") ^ Literal("/")
decimal_int = Word(nums)
hex_int = Literal("0x") + Word(hexnums)
integer = decimal_int ^ hex_int
unit_address = Word(hexnums)
property_name = Word(alphanums + ",._+?#")
label = Word(alphanums + "_")
label_creation = label + Literal(":")
string = dblQuotedString
stringlist = delimitedList(string)
node_path = Literal("/") + delimitedList(node_name, delim="/") + Optional(Literal("@") + unit_address)
reference = Literal("&") + (Literal("{") + node_path + Literal("}")) ^ label
directive = QuotedString(quoteChar="/") + Optional(property_name ^ node_name ^ reference ^ (integer * 2)) + Literal(";")

unary_operator = Word("~!", exact=1)
binary_operator = Word("+-*/&|^<>", exact=1) ^ Literal("<<") ^ Literal(">>") ^ Literal("&&") ^ Literal("||") ^ Literal("<=") ^ Literal(">=") ^ Literal("==") ^ Literal("!=")
unary_expr = unary_operator + integer
binary_expr = integer + binary_operator + integer
unit_arithmetic_expr = integer ^ unary_expr ^ binary_expr
arithmetic_expr = nestedExpr(Literal("("), Literal(")"), content=unit_arithmetic_expr)
ternary_expr = Literal("(") + (arithmetic_expr + Literal("?") + arithmetic_expr + Literal(":") + arithmetic_expr) + Literal(")")

array = Literal("<") + (arithmetic_expr ^ string ^ reference ^ label_creation) + Literal(">")
bytestring = Literal("[") + (Word(hexnums) ^ label_creation) + Literal("]")
property_assignment = property_name + Literal("=") + (array ^ bytestring ^ stringlist ^ label_creation) + Literal(";")

node_opener = Optional(label_creation) + node_name + Optional(Literal("@") + unit_address) + Literal("{")
node_closer = Literal("}") + Literal(";")
node_definition = nestedExpr(node_opener, node_closer, content=(property_assignment ^ directive))

devicetree = ZeroOrMore(directive ^ node_definition)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(devicetree.parseFile(sys.argv[1]))
