"""OSC Address Spaces and Address Pattern Matching.

Implements the following parts of the OSC 1.0 specification:

* OSC Address Spaces and OSC Addresses
* OSC Message Dispatching and Pattern Matching

See the ``_demo()`` function below for a usage example.

**Note:** Path-traversing wildcards (``//``) as specified by the OSC 1.1
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


def get_default_root():
    global _root
    if _root is None:
        _root = OSCAddressContainer("/")
    return _root


def _demo():
    def fn(*args):
        pass

    import sys

    root = get_default_root()
    root.register_method(fn, "/ops/math/add", "ii")
    root.register_method(fn, "/ops/math/sum", TYPETAGS_ANY)
    root.register_method(fn, "/ops/string/add", "ii")
    root.register_method(fn, "/ops/array/add", "ii")
    root.register_method(fn, "/ops/math/sub", "ii")

    print(root.match(*sys.argv[1:]))


if __name__ == "__main__":
    _demo()
