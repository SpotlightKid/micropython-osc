"""OSC Address Spaces and Address Pattern Matching.

Implements the following parts of the OSC 1.0 specification:

* OSC Address Spaces and OSC Addresses
* OSC Message Dispatching and Pattern Matching

See the unit tests in ``tests/ttest_dispatch.py`` for API usage examples.

**Note:** Path-traversing wildcards (``//``) as envisioned by the OSC 1.1
"specification" paper are **not** supported.

"""

import re
from fnmatch import filter as fnfilter


ALLOWED_ADDRESS_CHARS = re.compile(r'^[0-9a-zA-Z!"$%&' + "\\\\'" + r"()+.:;<=>@^_`|~-]+\Z")
TYPETAGS_ANY = "*"


def expand_curly_braces(s, offset=0):
    expansions = [s]
    while True:
        new_expansions = []

        for sn in expansions:
            start = sn.find("{")

            if start == -1:
                return expansions

            end = sn.find("}", start + 1)

            if end == -1:
                raise ValueError("Unmatched opening curly brace.")

            items = [
                item.strip()
                for item in sn[start + 1:end].split(",")
                if ALLOWED_ADDRESS_CHARS.match(item.strip())
            ]
            new_expansions.extend([(sn[:start] + item.strip() + sn[end + 1:]) for item in items])
        expansions = new_expansions


class OSCAddressContainer(dict):
    """
    Branch node in the OSC Address Space tree containing OSC Methods or
    sub-branches.

    """
    def __init__(self, name, parent=None):
        super().__init__()
        self.name = name
        self.parent = parent

    def add_container(self, name):
        self[name] = OSCAddressContainer(name, parent=self)

    def add_method(self, callable_, address, typetags=TYPETAGS_ANY):
        name = address.split("/")[-1]
        self[name] = OSCMethod(address, callable_, typetags=typetags, parent=self)

    def getroot(self):
        node = self

        while node.parent:
            node = node.parent

        return node

    def register_method(self, callable_, address, typetags=TYPETAGS_ANY):
        assert address.startswith("/")
        _, *parts, leaf = address.split("/")
        # Is an empty string for the address leaf part allowed, e.g. "/" or "/status/"?
        # No empty address parts allowed:
        assert all(parts)
        # all address parts must be printable ASCII strings
        # minus explicitly dis-allowed chars
        assert all(ALLOWED_ADDRESS_CHARS.match(part) for part in parts)

        node = self.getroot()

        for name in parts:
            if name not in node:
                node.add_container(name)
            node = node[name]

        node.add_method(callable_, address, typetags=typetags)

    def match(self, pattern, typetags=None, glob_matching=True, brace_expansion=True):
        assert pattern.startswith("/")
        _, *parts, leaf = pattern.split("/")
        assert all(parts)  # no empty address pattern parts allowed

        results = []
        to_check = [self.getroot()]

        while parts:
            ptn = parts.pop(0)

            branches = []
            for node in to_check:
                if glob_matching:
                    branches.extend(
                        self._check_branch(node, ptn, OSCAddressContainer, brace_expansion)
                    )
                elif ptn in node:
                    branches = [node[ptn]]

            to_check = branches

        for branch in to_check:
            if glob_matching:
                results.extend(
                    [
                        method
                        for method in self._check_branch(branch, leaf, OSCMethod)
                        if typetags is None or method.typetags in (TYPETAGS_ANY, typetags)
                    ]
                )
            elif leaf in branch:
                results.append(branch[leaf])

        return results

    @staticmethod
    def _check_branch(node, ptn, nodetype, brace_expansion=True):
        patterns = [ptn]

        if brace_expansion:
            try:
                patterns = expand_curly_braces(ptn)
            except ValueError:
                pass

        for ptn in patterns:
            for name in fnfilter(node.keys(), ptn):
                child = node[name]
                if isinstance(child, nodetype):
                    yield child


class OSCMethod:
    """
    A leaf node in the OSC Address Space tree wrapping the callable for an OSC
    Method.

    """
    __slots__ = ("name", "callable_", "typetags", "parent")

    def __init__(self, name, callable_, typetags=TYPETAGS_ANY, parent=None):
        self.name = name
        self.callable_ = callable_
        self.typetags = typetags
        self.parent = parent

    def __call__(self, *args, **kwargs):
        return self.callable_(*args, **kwargs)

    def __repr__(self):
        return f"<OSCMethod '{self.name}', {self.typetags}>"


_root = None


def get_global_root():
    """Return global OSC Address Space root OSCAdressContainer node instance.

    The root node is created on demand, when this function is first called and
    the tree will initially be unpopulated, i.e. have no branches or leaves.

    The global root node, as the name says, is a module global, so changes to
    the tree it is the root of, will be visible via all references to it
    retrieved via this function in the same program.

    To create a non-global OSC Adress Space tree, just create a new
    ``OSCAddressContainer`` instance like so:

        myroot = OSCAddressContainer(name="/")

    """
    global _root

    if _root is None:
        _root = OSCAddressContainer("/")

    return _root
