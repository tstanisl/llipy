"Unittests for llipy parser"

import unittest

import pyparsing

from llipy.llipy import (
    Array,
    Function,
    INT1, INT8, INT16, INT32, INT64,
    Pointer,
    Scalar,
    Struct,
    Type,
    VOID,
)

class TestType(unittest.TestCase):
    parser = Type.parser()
    def test(self):
        tests = [
            ('void', VOID, 0),
            ('i1', INT1, 1),
            ('i8', INT8, 1),
            ('i16', INT16, 2),
            ('i32', INT32, 4),
            ('i64', INT64, 8),
            ('i8*', Pointer(INT8), 4),
            ('i32**', Pointer(Pointer(INT32)), 4),
            ('{}', Struct(), 0),
            ('{i1}', Struct(INT1), 1),
            ('{{i1}}', Struct(Struct(INT1)), 1),
            ('{i8, i16}', Struct(INT8, INT16), 3),
            ('{i8*}', Struct(Pointer(INT8)), 4),
            ('[4 x i1]', Array(4, INT1), 4),
            ('[50 x [4 x i32]]', Array(50, Array(4, INT32)), 800),
            ('[1 x [2 x [3 x i64]]]', Array(1, Array(2, Array(3, INT64))), 48),
            ('{i8}*', Pointer(Struct(INT8)), 4),
            ('[2 x i1]*', Pointer(Array(2, INT1)), 4),
            ('i1 (i1)', Function(INT1, INT1), None),
            ('i1 ()', Function(INT1), None),
            ('void (i8, ...)', Function(VOID, INT8, variadic=True), None),
            ('void (...)', Function(VOID, variadic=True), None),
            ('void (i8, i16)*', Pointer(Function(VOID, INT8, INT16)), None),
            ('void ()*()', Function(Pointer(Function(VOID))), None),
        ]
        for txt, type_, size in tests:
            with self.subTest(val=txt):
                pval = self.parser.parseString(txt)[0]
                self.assertEqual(pval, type_)
                if size is not None:
                    self.assertEqual(len(pval), size)

if __name__ == '__main__':
    unittest.main()
