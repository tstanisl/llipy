"Unittests for llipy parser"

import unittest

import pyparsing

from llipy.llipy import (
    Array,
    Function,
    GlobalDef,
    INT1, INT8, INT16, INT32, INT64,
    Pointer,
    Scalar,
    Struct,
    Type,
    UNDEF,
    VOID,
    ZEROINIT,
)

class TestGlobalDef(unittest.TestCase):
    def test(self):
        parser = GlobalDef.parser()
        tests = [
            ('@f = global i8 0', '@f', INT8, 0),
            ('@.f = global i8 zeroinitializer', '@.f', INT8, ZEROINIT),
            ('@Ptr = constant i8* null', '@Ptr', Pointer(INT8), ZEROINIT),
            ('@x = global i8', '@x', INT8, UNDEF),
            ('@x = external global i8', '@x', INT8, UNDEF),
            ('@x = private global i1 0', '@x', INT1, 0),
            ('@x = default global i1 0', '@x', INT1, 0),
            ('@x = unnamed_addr global i1 0', '@x', INT1, 0),
            ('@x = global i1 0, align 1', '@x', INT1, 0),
            ('@x = global i1 0, !align !1', '@x', INT1, 0),
        ]
        for txt, name, type_, value in tests:
            with self.subTest(val=txt):
                res = parser.parseString(txt)[0]
                self.assertEqual(res.name, name)
                self.assertEqual(res.type, type_)
                self.assertEqual(res.value, value)

if __name__ == '__main__':
    unittest.main()
