"Parser for LLVM IR in human readable form (.ll) files."

from abc import ABCMeta, abstractmethod, abstractclassmethod
import functools

from pyparsing import (
    delimitedList,
    Empty,
    Keyword,
    MatchFirst,
    Regex,
    QuotedString,
)

def cached(fun):
    "Caching decorator"
    return functools.lru_cache()(fun)

def kw_of(keywords):
    """Helper to quickly define a set of alternative Keywords.
     Keywords are matched using MatchFirst."""
    return MatchFirst(Keyword(word) for word in keywords.split())

def commalist(entry):
    "Helper to define a comma separated list. The list can be empty."
    return delimitedList(entry) | Empty()

def kwobj(key, obj):
    "Creates a parser for given keyword that returns a given object"
    helper = lambda s, l, t, ret=obj: ret
    return Keyword(key).setParseAction(helper)

NUMBER = Regex(r'-?\d+').setParseAction(lambda tok: int(tok[0]))
QSTR = QuotedString('"', escChar='\\').setParseAction(lambda tok: tok[0])
LOCAL = Regex(r'%[\w.]+').setParseAction(lambda tok: tok[0])

class Node(metaclass=ABCMeta):
    "Base class for all llipy nodes"
    @abstractclassmethod
    def parser(cls):
        "Returns a PyParsing parser for given class"

class Type(Node):
    "ABC covering all LLIPY type nodes"
    @abstractmethod
    def __len__(self):
        "Size of object in bytes"

    @abstractmethod
    def offset(self, index):
        "Offset of indexed property property in bytes"

class ScalarType(Type):
    "All types without any substructure. Covers void and integer types"
    def __init__(self, bits):
        self._bits = bits

    def __len__(self):
        return (self._bits + 7) // 8

    def offset(self, index):
        assert index == 0
        return 0

    @classmethod
    def parser(cls):
        types = {
            'void': VOID,
            'i1': INT1,
            'i8': INT8,
            'i16': INT16,
            'i32': INT32,
            'i64': INT64,
        }

        return MatchFirst(Keyword(key).setParseAction(lambda *_, val=val: val)
                          for key, val in types.items())

VOID = ScalarType(0)
INT1 = ScalarType(1)
INT8 = ScalarType(8)
INT16 = ScalarType(16)
INT32 = ScalarType(32)
INT64 = ScalarType(64)
