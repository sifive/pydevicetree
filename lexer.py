from pyparsing import *

node_name = Word(alphanums + ",.-+_") ^ Literal("/")
decimal_int = Word(nums)
hex_int = Combine(Literal("0x") + Word(hexnums))
integer = decimal_int ^ hex_int
unit_address = Word(hexnums)
property_name = Word(alphanums + ",.-_+?#")
label = Word(alphanums + "_")
label_creation = Combine(label + Literal(":"))
string = QuotedString(quoteChar='"', unquoteResults=False)
stringlist = delimitedList(string)
node_path = Combine(Literal("/") + delimitedList(node_name, delim="/") + Optional(Literal("@") + unit_address))
reference = Combine(Literal("&") + ((Literal("{") + node_path + Literal("}")) ^ label))
directive = QuotedString(quoteChar="/", unquoteResults=False) + Optional(property_name ^ node_name ^ reference ^ (integer * 2)) + Literal(";")

# todo: arithmetic expressions
arith_expr = integer

array = Literal("<") + ZeroOrMore(arith_expr ^ string ^ reference ^ label_creation) + Literal(">")
bytestring = Literal("[") + (Word(hexnums) ^ label_creation) + Literal("]")
property_assignment = property_name + Optional(Literal("=") + (array ^ bytestring ^ stringlist ^ label_creation)) + Literal(";")

node_opener = Optional(label_creation).setResultsName("label") + node_name("name") + Optional(Literal("@").suppress() + unit_address("address")) + Literal("{")
node_closer = Literal("}") + Literal(";")
node_definition = Forward()
node_definition << node_opener + ZeroOrMore(property_assignment ^ directive ^ node_definition).setResultsName("children") + node_closer

devicetree = ZeroOrMore(directive ^ node_definition)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        devicetree.parseFile(sys.argv[1]).pprint()
