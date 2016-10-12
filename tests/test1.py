"Unittests for llipy parser"

import unittest

import pyparsing

from llipy.llipy import (
    ArrayType,
    INT1, INT8, INT16, INT32, INT64,
    PointerType,
    ScalarType,
    StructType,
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
            ('i8*', PointerType(INT8), 4),
            ('i32**', PointerType(PointerType(INT32)), 4),
            ('{}', StructType(), 0),
            ('{i1}', StructType(INT1), 1),
            ('{{i1}}', StructType(StructType(INT1)), 1),
            ('{i8, i16}', StructType(INT8, INT16), 3),
            ('{i8*}', StructType(PointerType(INT8)), 4),
            ('[4 x i1]', ArrayType(4, INT1), 4),
            ('[50 x [4 x i32]]', ArrayType(50, ArrayType(4, INT32)), 800),
            ('[1 x [2 x [3 x i64]]]', ArrayType(1, ArrayType(2, ArrayType(3, INT64))), 48),
            ('{i8}*', PointerType(StructType(INT8)), 4),
            ('[2 x i1]*', PointerType(ArrayType(2, INT1)), 4),
        ]
        for txt, type_, size in tests:
            with self.subTest(val=txt):
                pval = self.parser.parseString(txt)[0]
                self.assertEqual(pval, type_)
                self.assertEqual(len(pval), size)

if __name__ == '__main__':
    unittest.main()
