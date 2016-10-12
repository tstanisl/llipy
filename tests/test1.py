"Unittests for llipy parser"

import unittest

import pyparsing

from llipy.llipy import (
    ArrayType,
    INT1, INT8, INT16, INT32, INT64,
    ScalarType,
    StructType,
    Type,
    VOID,
)

class TestScalarTypes(unittest.TestCase):
    parser = ScalarType.parser()
    def test(self):
        tests = [
            ('void', VOID),
            ('i1', INT1),
            ('i8', INT8),
            ('i16', INT16),
            ('i32', INT32),
            ('i64', INT64),
        ]
        for txt, obj in tests:
            with self.subTest(val=txt):
                pval = self.parser.parseString(txt)[0]
                self.assertEqual(pval, obj)

class TestArrayType(unittest.TestCase):
    parser = ArrayType.parser()
    def test(self):
        tests = [
            ('[4 x i1]', INT1, (4,)),
            ('[50 x [4 x i32]]', INT32, (50, 4)),
            ('[1 x [1 x [1 x i64]]]', INT64, (1, 1, 1)),
        ]
        def analyze(arr):
            "Extracts base type and dimensions from ArrayType"
            if isinstance(arr, ArrayType):
                slots = arr.slots()
                etype, dim = analyze(arr.etype())
                return etype, (slots,) + dim
            return arr, ()

        for txt, etype, dim in tests:
            with self.subTest(val=txt):
                pval = self.parser.parseString(txt)[0]
                self.assertTrue(isinstance(pval, ArrayType))

                petype, pdim = analyze(pval)

                self.assertEqual(etype, petype)
                self.assertEqual(dim, pdim)

class TestStructType(unittest.TestCase):
    parser = StructType.parser()
    def test(self):
        tests = [
            ('{}', (), 0),
            ('{i1}', (INT1,), 1),
            ('{i8, i16}', (INT8, INT16), 3),
        ]
        for txt, etypes, size in tests:
            with self.subTest(val=txt):
                pval = self.parser.parseString(txt)[0]
                self.assertTrue(isinstance(pval, StructType))
                self.assertEqual(pval.slots(), len(etypes))

                for idx, etype in enumerate(etypes):
                    self.assertEqual(pval.etype(idx), etype)

if __name__ == '__main__':
    unittest.main()
