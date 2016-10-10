"Unittests for llipy parser"

import unittest

import pyparsing

import llipy.llipy as ll

class TestScalarTypes(unittest.TestCase):
    parser = ll.ScalarType.parser()
    def test(self):
        tests = [
            ('void', ll.VOID),
            ('i1', ll.INT1),
            ('i8', ll.INT8),
            ('i16', ll.INT16),
            ('i32', ll.INT32),
            ('i64', ll.INT64),
        ]
        for txt, obj in tests:
            with self.subTest(val=txt):
                pval = self.parser.parseString(txt)[0]
                self.assertEqual(pval, obj)

class TestArrayType(unittest.TestCase):
    parser = ll.ArrayType.parser()
    def test(self):
        tests = [
            ('[4 x i1]', ll.INT1, (4,)),
            ('[50 x [4 x i32]]', ll.INT32, (50, 4)),
            ('[1 x [1 x [1 x i64]]]', ll.INT64, (1, 1, 1)),
        ]
        def analyze(arr):
            "Extracts base type and dimensions from ArrayType"
            if isinstance(arr, ll.ArrayType):
                slots = arr.slots()
                etype, dim = analyze(arr.etype())
                return etype, (slots,) + dim
            return arr, ()

        for txt, etype, dim in tests:
            with self.subTest(val=txt):
                pval = self.parser.parseString(txt)[0]
                self.assertTrue(isinstance(pval, ll.ArrayType))

                petype, pdim = analyze(pval)

                self.assertEqual(etype, petype)
                self.assertEqual(dim, pdim)

class TestStructType(unittest.TestCase):
    parser = ll.StructType.parser()
    def test(self):
        tests = [
            ('{}', (), 0),
            ('{i1}', (ll.INT1,), 1),
            ('{i8, i16}', (ll.INT8, ll.INT16), 3),
        ]
        for txt, etypes, size in tests:
            with self.subTest(val=txt):
                pval = self.parser.parseString(txt)[0]
                self.assertTrue(isinstance(pval, ll.StructType))
                self.assertEqual(pval.slots(), len(etypes))

                for idx, etype in enumerate(etypes):
                    self.assertEqual(pval.etype(idx), etype)

if __name__ == '__main__':
    unittest.main()
