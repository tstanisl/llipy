"Parser for LLVM IR in human readable form (.ll) files."

import pyparsing as pp

def _prepare_parser():
    number = pp.Regex(r'-?\d+')
    local = pp.Regex(r'%[A-Za-z0-9._]+')
    glob = pp.Regex(r'@[A-Za-z0-9._]+')

    keywords = lambda keywords: pp.MatchFirst(word for word in keywords.split())

    label = local + ':'

    unused_def = keywords('target declare attributes !') + pp.restOfLine

    definition = unused_def
    llvm = pp.ZeroOrMore(definition)

    comment = ';' + pp.restOfLine
    llvm.ignore(comment)

    return llvm

parser = _prepare_parser()
