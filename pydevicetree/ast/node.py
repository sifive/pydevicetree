#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

import re
import os
from typing import List, Union, Optional, Iterable, Callable, Any, cast, Pattern

from pydevicetree.ast.helpers import formatLevel
from pydevicetree.ast.property import Property, PropertyValues
from pydevicetree.ast.directive import Directive

# Type signature for elements passed to Devicetree constructor
ElementList = Iterable[Union['Node', Property, Directive]]

# Callback type signatures for Devicetree.match() and Devicetree.chosen()
MatchCallback = Optional[Callable[['Node'], None]]
ChosenCallback = Optional[Callable[[PropertyValues], None]]

class Node:
    """Represents a Devicetree Node

    A Devicetree Node generally takes the form

        [label:] node-name@unit-address {
            [directives]
            [properties]
            [child nodes]
        };

    The structure formed by creating trees of Nodes is the bulk of any Devicetree. As the naming
    system implies, then, each node roughly corresponds to some conceptual device, subsystem of
    devices, bus, etc.

    Devices can be referenced by label or by path, and are generally uniquely identified by a
    collection of string identifiers assigned to the "compatible" property.

    For instance, a UART device might look like

        uart0: uart@10013000 {
            compatible = "sifive,uart0";
            reg = <0x10013000 0x1000>;
            reg-names = "control";
            interrupt-parent = <&plic>;
            interrupts = <3>;
            clocks = <&busclk>;
            status = "okay";
        };

    This node can be identified in the following ways:

        - By label: uart0
        - By path: /path/to/uart@10013000
        - By name: uart@10013000 (for example when referenced in a /delete-node/ directive)
    """
    # pylint: disable=too-many-arguments
    def __init__(self, name: str, label: Optional[str] = None, address: Optional[int] = None,
                 properties: List[Property] = None, directives: List[Directive] = None,
                 children: List['Node'] = None):
        """Initializes a Devicetree Node

        Also evaluates the /delete-node/ and /delete-property/ directives found in the node
        and deletes the respective nodes and properties.
        """
        self.name = name
        self.parent = None # isinstance: Optional['Node']

        self.label = label
        self.address = address
        self.properties = properties
        self.directives = directives
        self.children = children

        for d in self.directives:
            name = d.directive
            if name == "/delete-node/":
                option = d.options
                node = self.get_by_reference(option)
                if node:
                    del self.children[self.children.index(node)]
                else:
                    node = self.__get_child_by_handle(option)
                    if node:
                        del self.children[self.children.index(node)]
            elif name == "/delete-property/":
                option = d.options
                # pylint: disable=cell-var-from-loop
                properties = list(filter(lambda p: p.name == option, self.properties))
                if properties:
                    del self.properties[self.properties.index(properties[0])]

    def __repr__(self) -> str:
        if self.address:
            return "<Node %s@%x>" % (self.name, self.address)
        return "<Node %s>" % self.name

    def __str__(self) -> str:
        return self.to_dts()

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.address == other.address

    def __hash__(self):
        return hash((self.name, self.address))

    @staticmethod
    def from_dts(source: str) -> 'Node':
        """Create a node from Devicetree Source"""
        # pylint: disable=import-outside-toplevel,cyclic-import
        from pydevicetree.source import parseNode
        return parseNode(source)

    def add_child(self, node: 'Node', merge: bool = True):
        """Add a child node and merge it into the tree"""
        node.parent = self
        self.children.append(node)
        if merge:
            self.merge_tree()

    def to_dts(self, level: int = 0) -> str:
        """Format the subtree starting at the node as Devicetree Source"""
        out = ""
        if isinstance(self.address, int) and self.label:
            out += formatLevel(level,
                               "%s: %s@%x {\n" % (self.label, self.name, self.address))
        elif isinstance(self.address, int):
            out += formatLevel(level, "%s@%x {\n" % (self.name, self.address))
        elif self.label:
            out += formatLevel(level, "%s: %s {\n" % (self.label, self.name))
        elif self.name != "":
            out += formatLevel(level, "%s {\n" % self.name)

        for d in self.directives:
            out += d.to_dts(level + 1)
        for p in self.properties:
            out += p.to_dts(level + 1)
        for c in self.children:
            out += c.to_dts(level + 1)

        if self.name != "":
            out += formatLevel(level, "};\n")

        return out

    def merge_tree(self):
        """Recursively merge child nodes into a single tree

        Parsed Devicetrees can describe the same tree multiple times, adding nodes and properties
        each time. After parsing, this method is called to recursively merge the tree.
        """
        partitioned_children = []
        for n in self.children:
            partitioned_children.append([e for e in self.children if e == n])

        new_children = []
        for part in partitioned_children:
            first = part[0]
            rest = part[1:]
            if first not in new_children:
                for n in rest:
                    first.merge(n)
                new_children.append(first)

        self.children = new_children

        for n in self.children:
            n.merge_tree()

    def merge(self, other: 'Node'):
        """Merge the contents of a node into this node.

        Used by Node.merge_trees()
        """
        if not self.label and other.label:
            self.label = other.label
        self.properties += other.properties
        self.directives += other.directives
        self.children += other.children

    def get_path(self) -> str:
        """Get the path of a node (ex. /cpus/cpu@0)"""
        if self.name == "/":
            return ""
        if self.parent is None:
            return "/" + self.name
        if isinstance(self.address, int):
            return self.parent.get_path() + "/" + self.name + "@" + ("%x" % self.address)
        return self.parent.get_path() + "/" + self.name

    def get_by_reference(self, reference: str) -> Optional['Node']:
        """Get a node from the subtree by reference (ex. &label, &{/path/to/node})"""
        match_path = re.match(r"&{(?P<path>[/\w\d,\._\+-@]*)}", reference, re.ASCII)
        match_label = re.match(r"&(?P<label>[\d\w_]*)", reference, re.ASCII)

        if match_path:
            return self.get_by_path(match_path.group("path"))
        if match_label:
            return self.get_by_label(match_label.group("label"))
        return None

    def get_by_label(self, label: str) -> Optional['Node']:
        """Get a node from the subtree by label"""
        matching_nodes = list(filter(lambda n: n.label == label, self.child_nodes()))
        if len(matching_nodes) != 0:
            return matching_nodes[0]
        return None

    def __get_child_by_handle(self, handle: str) -> Optional['Node']:
        """Get a child node by name or name and unit address"""
        if '@' in handle:
            name, addr_s = handle.split('@')
            address = int(addr_s, base=16)
            nodes = list(filter(lambda n: n.name == name and n.address == address, self.children))
        else:
            name = handle
            nodes = list(filter(lambda n: n.name == name, self.children))

        if not nodes:
            return None
        if len(nodes) > 1:
            raise Exception("Handle %s is ambiguous!" % handle)
        return nodes[0]

    def get_by_path(self, path: str) -> Optional['Node']:
        """Get a node in the subtree by path"""
        node_handles = list(filter(lambda s: s != '', path.split("/")))

        if not node_handles:
            return self

        node = self.__get_child_by_handle(node_handles[0])

        if node:
            return node.get_by_path('/'.join(node_handles[1:]))
        return None

    def match(self, compatible: Pattern, func: MatchCallback = None) -> List['Node']:
        """Get a node from the subtree by compatible string

        Accepts a regular expression to match one of the strings in the compatible property.
        """
        regex = re.compile(compatible)

        def match_compat(node: Node) -> bool:
            compatibles = node.get_fields("compatible")
            if compatibles is not None:
                return any(regex.match(c) for c in compatibles)
            return False

        nodes = list(filter(match_compat, self.child_nodes()))

        if func is not None:
            for n in nodes:
                func(n)

        return nodes

    def child_nodes(self) -> Iterable['Node']:
        """Get an iterable over all the nodes in the subtree"""
        for n in self.children:
            yield n
            for m in n.child_nodes():
                yield m

    def remove_child(self, node):
        """Remove a child node"""
        del self.children[self.children.index(node)]

    def get_fields(self, field_name: str) -> Optional[PropertyValues]:
        """Get all the values of a property"""
        for p in self.properties:
            if p.name == field_name:
                return p.values
        return None

    def get_field(self, field_name: str) -> Any:
        """Get the first value of a property"""
        fields = self.get_fields(field_name)
        if fields is not None:
            if len(cast(PropertyValues, fields)) != 0:
                return fields[0]
        return None

    def address_cells(self):
        """Get the number of address cells"""
        cells = self.get_field("#address-cells")
        if cells is not None:
            return cells
        if self.parent is not None:
            return self.parent.address_cells()
        # No address cells found
        return 0

    def size_cells(self):
        """Get the number of size cells"""
        cells = self.get_field("#size-cells")
        if cells is not None:
            return cells
        if self.parent is not None:
            return self.parent.size_cells()
        # No size cells found
        return 0

class NodeReference(Node):
    """A NodeReference is used to extend the definition of a previously-defined Node

    NodeReferences are commonly used by Devicetree "overlays" to extend the properties of a node
    or add child devices, such as to a bus like I2C.
    """
    def __init__(self, reference: str, properties: List[Property] = None,
                 directives: List[Directive] = None, children: List[Node] = None):
        """Instantiate a Node identified by reference to another node"""
        self.reference = reference
        Node.__init__(self, name="", properties=properties, directives=directives,
                      children=children)

    def __repr__(self) -> str:
        return "<NodeReference %s>" % self.reference

    def resolve_reference(self, tree: 'Devicetree') -> Node:
        """Given the full tree, get the node being referenced"""
        node = tree.get_by_reference(self.reference)
        if node is None:
            raise Exception("Node reference %s cannot be resolved" % self.reference)
        return cast(Node, node)

class Devicetree(Node):
    """A Devicetree object describes the full Devicetree tree

    This class encapsulates both the tree itself (starting at the root node /) and any Directives
    or nodes which exist at the top level of the Devicetree Source files.

    Devicetree Source files can be parsed by calling Devicetree.parseFile().
    """
    def __init__(self, elements: ElementList = None):
        """Instantiate a Devicetree with the list of parsed elements

        Resolves all reference nodes and merges the tree to combine all identical nodes.
        """
        properties = [] # type: List[Property]
        directives = [] # type: List[Directive]
        children = [] # type: List[Node]

        for e in elements:
            if isinstance(e, Node):
                children.append(cast(Node, e))
            elif isinstance(e, Property):
                properties.append(cast(Property, e))
            elif isinstance(e, Directive):
                directives.append(cast(Directive, e))

        Node.__init__(self, name="",
                      properties=properties, directives=directives, children=children)

        for node in self.children:
            node.parent = self

        reference_nodes = filter(lambda node: isinstance(node, NodeReference), self.all_nodes())
        for refnode in reference_nodes:
            node = refnode.resolve_reference(self)

            refnode.parent.remove_child(refnode)

            node.properties += refnode.properties
            node.directives += refnode.directives
            node.children += refnode.children

        self.merge_tree()

    def __repr__(self) -> str:
        name = self.root().get_field("compatible")
        return "<Devicetree %s>" % name

    def to_dts(self, level: int = 0) -> str:
        """Convert the tree back to Devicetree Source"""
        out = ""

        for d in self.directives:
            out += d.to_dts()
        for p in self.properties:
            out += p.to_dts()
        for c in self.children:
            out += c.to_dts()

        return out

    def get_by_path(self, path: str) -> Optional[Node]:
        """Get a node in the tree by path (ex. /cpus/cpu@0)"""
        return self.root().get_by_path(path)

    @staticmethod
    def parseFile(filename: str, followIncludes: bool = False) -> 'Devicetree':
        """Parse a file and return a Devicetree object"""
        # pylint: disable=import-outside-toplevel,cyclic-import
        from pydevicetree.source import parseTree
        with open(filename, 'r') as f:
            contents = f.read()
        pwd = os.path.dirname(filename) + "/"
        return parseTree(contents, pwd, followIncludes)

    def all_nodes(self) -> Iterable[Node]:
        """Get an iterable over all nodes in the tree"""
        return self.child_nodes()

    def root(self) -> Node:
        """Get the root node of the tree"""
        for n in self.all_nodes():
            if n.name == "/":
                return n
        raise Exception("Devicetree has no root node!")

    def chosen(self, property_name: str, func: ChosenCallback = None) -> Optional[PropertyValues]:
        """Get the values associated with one of the properties in the chosen node"""
        def match_chosen(node: Node) -> bool:
            return node.name == "chosen"

        for n in filter(match_chosen, self.all_nodes()):
            for p in n.properties:
                if p.name == property_name:
                    if func is not None:
                        func(p.values)
                    return p.values

        return None
