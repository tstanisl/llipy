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

if __name__ == '__main__':
    unittest.main()
