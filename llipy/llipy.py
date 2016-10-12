"Parser for LLVM IR in human readable form (.ll) files."

from abc import ABCMeta, abstractmethod, abstractclassmethod
import functools

from pyparsing import (
    delimitedList,
    Empty,
    Forward,
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
    parser = delimitedList(entry) | Empty()
    # parser.setParseAction(lambda *t: print(t))
    return parser

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

    @classmethod
    def parser(cls):
        if not hasattr(cls, '_parser'):
            cls._parser = Forward()
            cls._parser <<= (
                ScalarType.parser() |
                ArrayType.parser() |
                StructType.parser()
            )
        return cls._parser

class ScalarType(Type):
    "All types without any substructure. Covers void and integer types"

    def __init__(self, bits):
        self._bits = bits

    def __len__(self):
        return (self._bits + 7) // 8

    @classmethod
    @cached
    def parser(cls):
        types = (('void', VOID),
                 ('i1', INT1),
                 ('i8', INT8),
                 ('i16', INT16),
                 ('i32', INT32),
                 ('i64', INT64))

        return MatchFirst(kwobj(key, obj) for key, obj in types)

VOID = ScalarType(0)
INT1 = ScalarType(1)
INT8 = ScalarType(8)
INT16 = ScalarType(16)
INT32 = ScalarType(32)
INT64 = ScalarType(64)

class CompoundType(Type):
    "Abstract class for compund types"

    @abstractmethod
    def offset(self, index):
        "Offset of indexed property property in bytes"

    @abstractmethod
    def slots(self):
        "Number of slots in the compound"

    @abstractmethod
    def etype(self, index):
        "Type of element at given index"

class ArrayType(CompoundType):
    "Node dedicated to array types"
    def __init__(self, slots, etype):
        self._slots = slots
        self._etype = etype

    def __len__(self):
        return self._slots * len(self._etype)

    def offset(self, index):
        assert 0 <= index < len(self)
        return index * len(self._etype)

    def slots(self):
        return self._slots

    def etype(self, index=0):
        return self._etype

    @classmethod
    @cached
    def parser(cls):
        ret = '[' - NUMBER - 'x' - Type.parser() + ']'
        ret.setParseAction(lambda t: ArrayType(t[1], t[3]))
        return ret

class StructType(CompoundType):
    "Compound type similat to C-struct"
    def __init__(self, etypes):
        self._etypes = etypes
        self._size = sum(len(etype) for etype in etypes)

    def __len__(self):
        return self._size

    @cached
    def offset(self, index):
        return sum(len(etype) for etype in self._etypes[:index])

    def slots(self):
        return len(self._etypes)

    def etype(self, index):
        return self._etypes[index]

    @classmethod
    @cached
    def parser(cls):
        ret = '{' - commalist(Type.parser()) - '}'
        return ret.setParseAction(lambda t: StructType(t[1:-1]))
