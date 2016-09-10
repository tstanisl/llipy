"Parser for LLVM IR in human readable form (.ll) files."

from pyparsing import (
    MatchFirst,
    Regex,
    restOfLine,
    ZeroOrMore,
)

def _prepare_parser():
    number = Regex(r'-?\d+')
    local = Regex(r'%[A-Za-z0-9._]+')
    glob = Regex(r'@[A-Za-z0-9._]+')

    keywords = lambda keywords: MatchFirst(word for word in keywords.split())

    label = local + ':'

    unused_def = keywords('target declare attributes !') + restOfLine

    definition = unused_def
    llvm = ZeroOrMore(definition)

    comment = ';' + restOfLine
    llvm.ignore(comment)

    return llvm

parser = _prepare_parser()
