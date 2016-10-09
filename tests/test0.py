"Unittests for llipy parser"

import unittest

import pyparsing

import llipy.llipy as ll

class TestNUMBER(unittest.TestCase):
    parser = ll.NUMBER

    def test_pass(self):

        values = ["-14", "-1", "1", "9", "12345"]
        for val in values:
            with self.subTest(val=val):
                val0 = self.parser.parseString(val, True)[0]
                val1 = int(val)
                self.assertEqual(val0, val1)

    def test_fail(self):
        values = ["", "abv", "12.32", "1+2", "-5f", "0x12"]
        for val in values:
            with self.subTest(val=val),\
                 self.assertRaises(pyparsing.ParseException):
                self.parser.parseString(val, True)


if __name__ == '__main__':
    unittest.main()
