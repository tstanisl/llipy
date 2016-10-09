"Parser for LLVM IR in human readable form (.ll) files."

import abc

from pyparsing import (
    delimitedList,
    Empty,
    Keyword,
    MatchFirst,
    Regex,
)

def kw_of(keywords):
    """Helper to quickly define a set of alternative Keywords.
     Keywords are matched using MatchFirst."""
    return MatchFirst(Keyword(word) for word in keywords.split())

def commalist(entry):
    "Helper to define a comma separated list. The list can be empty."
    return delimitedList(entry) | Empty()

class Node(metaclass=abc.ABCMeta):
    "Base class for all llipy nodes"
    @abc.abstractclassmethod
    def parser(cls):
        "Returns a PyParsing parser for given class"

NUMBER = Regex(r'-?\d+').setParseAction(lambda tok: int(tok[0]))

