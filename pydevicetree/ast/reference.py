#!/usr/bin/env python3
# Copyright (c) 2019 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

from typing import Union, Iterator, Optional

class Label:
    """A Label is a unique identifier for a Node

    For example, the following node has the label "uart0":

        uart0: uart@10013000 {
            ...
        };
    """
    def __init__(self, name: str):
        """Create a Label"""
        self.name = name

    def __repr__(self) -> str:
        return "<Label " + self.name + ">"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Label):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

    def to_dts(self) -> str:
        """Format the label in Devicetree Source format"""
        return self.name + ":"

class Path:
    """A Path uniquely identifies a Node by its parents and (optionally) unit address"""
    def __init__(self, path: str, address: Optional[int] = None):
        """Create a path out of a string"""
        self.path = list(filter(lambda s: s != '', path.split('/')))
        self.address = address

    def to_dts(self) -> str:
        """Format the Path in Devicetree Source format"""
        if self.address:
            return '/%s@%x' % ('/'.join(self.path), self.address)
        return '/' + '/'.join(self.path)

    def __repr__(self) -> str:
        return "<Path " + self.to_dts() + ">"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Path):
            return self.to_dts() == other.to_dts()
        if isinstance(other, str):
            if ("@" not in other) and (self.address is not None):
                return self.to_dts().split("@")[0] == other
            return self.to_dts() == other
        return False

    def __iter__(self) -> Iterator[str]:
        return iter(['/'] + self.path)

    def replace(self, old: str, new: str) -> 'Path':
        """Replace any elements of the path which match 'old' with a new element 'new'"""
        path = [e.replace(old, new) for e in self.path]
        return Path('/' + '/'.join(path), self.address)


class Reference:
    """A Reference is a Devicetree construct which points to a Node in the tree

    The following are types of references:

        - A reference to a label:

            &my-label;

        - A reference to a node by path:

            &{/path/to/node@deadbeef}

    This is the parent class for both types of references, LabelReference and PathReference
    """
    # pylint: disable=no-self-use
    def to_dts(self) -> str:
        """Format the Reference in Devicetree Source format"""
        return ""

class LabelReference(Reference):
    """A LabelReference is a reference to a Node by label"""
    def __init__(self, label: Union[Label, str]):
        """Create a LabelReference from a Label or string"""
        if isinstance(label, Label):
            self.label = label
        elif isinstance(label, str):
            self.label = Label(label)

    def __repr__(self) -> str:
        return "<LabelReference " + self.to_dts() + ">"

    def to_dts(self) -> str:
        """Format the LabelReference in Devicetree Source format"""
        return "&" + self.label.name

class PathReference(Reference):
    """A PathReference is a reference to a Node by path"""
    def __init__(self, path: Union[Path, str]):
        """Create a PathReference from a Path or string"""
        if isinstance(path, Path):
            self.path = path
        elif isinstance(path, str):
            self.path = Path(path)

    def __repr__(self) -> str:
        return "<PathReference " + self.to_dts() + ">"

    def to_dts(self) -> str:
        """Format the PathReference in Devicetree Source format"""
        return "&{" + self.path.to_dts() + "}"
