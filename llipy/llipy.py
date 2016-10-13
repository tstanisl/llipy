"Parser for LLVM IR in human readable form (.ll) files."

from abc import ABCMeta, abstractmethod, abstractclassmethod
import functools
from itertools import accumulate

from pyparsing import (
    delimitedList,
    Empty,
    Forward,
    Keyword,
    MatchFirst,
    Optional,
    Regex,
    QuotedString,
    Suppress,
    ZeroOrMore,
)

def cached(fun):
    "Caching decorator"
    return functools.lru_cache()(fun)

def kwsof(keywords, default=None):
    """Helper to quickly define a set of alternative Keywords.
     Keywords are matched using MatchFirst."""
    ret = MatchFirst(Keyword(word) for word in keywords.split())
    return ret if default is None else Optional(ret, default)

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
QSTR = QuotedString('"', escChar='\\')
LOCAL = Regex(r'%[\w.]+')

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

    @staticmethod
    def _parser_tail(toks):
        "Post processing of tail type"
        #print('tail:', toks[1:])
        # pylint: disable=redefined-variable-type
        ret = toks[0]
        for tok in toks[1:]:
            if tok == '*':
                ret = Pointer(ret)
            else:
                assert isinstance(tok, ArgumentTypes)
                ret = Function(ret, *tok.args, variadic=tok.variadic)
        # pylint: enable=redefined-variable-type
        return ret

    @classmethod
    def parser(cls):
        if not hasattr(cls, '_parser'):
            cls._parser = Forward()
            func_or_ptr = '*' | ArgumentTypes.parser()
            cls._parser <<= (
                Scalar.parser() |
                Array.parser() |
                Struct.parser()
            ) + ZeroOrMore(func_or_ptr)
            cls._parser.setParseAction(cls._parser_tail)
        return cls._parser

    def __eq__(self, other):
        if not isinstance(other, Type):
            return NotImplemented
        return self is other

class Scalar(Type):
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

VOID = Scalar(0)
INT1 = Scalar(1)
INT8 = Scalar(8)
INT16 = Scalar(16)
INT32 = Scalar(32)
INT64 = Scalar(64)

class Compound(Type):
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

class Array(Compound):
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
        ret.setParseAction(lambda t: Array(t[1], t[3]))
        return ret

    def __eq__(self, other):
        if not isinstance(other, Array):
            return False
        return self.slots() == other.slots() and self.etype() == other.etype()

class Struct(Compound):
    "Compound type similat to C-struct"
    def __init__(self, *etypes):
        self.etypes = etypes
        self._offsets = (0,)
        self._offsets += tuple(accumulate(len(etype) for etype in etypes))

    def __len__(self):
        return self._offsets[-1]

    def offset(self, index):
        return self._offsets[index]

    def slots(self):
        return len(self.etypes)

    def etype(self, index):
        return self.etypes[index]

    @classmethod
    @cached
    def parser(cls):
        ret = '{' - commalist(Type.parser()) - '}'
        return ret.setParseAction(lambda t: Struct(*t[1:-1]))

    def __eq__(self, other):
        if not isinstance(other, Struct):
            return False
        return self.etypes == other.etypes

class Pointer(Type):
    "Pointer types."
    def __init__(self, pointee):
        self.pointee = pointee

    def __len__(self):
        return 4

    @classmethod
    def parser(cls):
        raise NotImplementedError

    def __eq__(self, other):
        if not isinstance(other, Pointer):
            return False
        return self.pointee == other.pointee

class ArgumentTypes(Node):
    "Helper class for list of argument types"
    def __init__(self, *args):
        #print('ArgumentTypes:', args)
        if args and args[-1] == '...':
            self.variadic = True
            self.args = args[:-1]
        else:
            self.variadic = False
            self.args = args

    @classmethod
    def parser(cls):
        args = commalist(Type.parser()) - Optional(Suppress(',') + '...')
        ret = '(' - ('...' | args) - ')'
        return ret.setParseAction(lambda t: ArgumentTypes(*t[1:-1]))

class Function(Type):
    "Type of Function as value, defined by its arguments and return value"
    def __init__(self, ret_type, *args, variadic=False):
        #print('Function:', ret_type, args, variadic)
        self.ret_type = ret_type
        self.args = args
        self.variadic = variadic

    def __len__(self):
        # Size of function is undefined, thus raising exception
        raise ValueError

    @classmethod
    def parser(cls):
        raise NotImplementedError

    def __eq__(self, other):
        if not isinstance(other, Function):
            return False
        return self.ret_type == other.ret_type and \
               self.args == other.args and \
               self.variadic == other.variadic

class Typedef(Node):
    "Node with definition of the type"
    def __init__(self, name, type_):
        self.name = name
        self.type_ = type_

    @classmethod
    def parser(cls):
        opaque = kwobj('opaque', VOID)
        ret = LOCAL - '=' - Keyword('type') - (opaque | Type.parser())
        return ret.setParseAction(lambda t: Typedef(t[0], t[3]))

class Constant(Node):
    "Abstraction for values"
    @classmethod
    def parser(cls):
        return NUMBER
