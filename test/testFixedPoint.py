#!/usr/bin/python
# unit-tests for simple fixed-point Python module
# $Revision$, $Date$
# RW Penney, January 2006

import sys, unittest
sys.path.insert(0, '..')
import FixedPoint


class FixedPointTest(unittest.TestCase):
    def setUp(self):
        pass
        #print "setting up"

    def tearDown(self):
        pass
        #print "tearing down"

    def testLongRounding(self):
        """long-integers should round towards minus infinity"""
        for base in range(2, 8):
            for step in range(1, 5):
                for inc in range(1, base):
                    pos = long((base * step) + inc)
                    self.assertEqual(long(step), (pos / base))
                    neg = long((base * -step) - inc)
                    self.assertEqual(long(-step - 1), (neg / base))


    def testAddition(self):
        """addition operators should promote & commute"""
        scale = 0.125
        for x in range(-16, 16):
            fpx = FixedPoint.FPnum(x * scale)
            for y in range(-32, 32):
                fpy = FixedPoint.FPnum(y * scale)
                fpa = FixedPoint.FPnum((x + y) * scale)

                # compute various forms of a = (x + y):

                self.assertEqual(fpa, fpx + fpy)
                self.assertEqual(fpa, fpy + fpx)
                self.assertEqual((x + y) * scale, float(fpx + fpy))

                tmp = FixedPoint.FPnum(fpx)
                tmp += fpy
                self.assertEqual(fpa, tmp)

                tmp = float(x * scale) + fpy
                self.assertEqual(fpa, tmp)

                tmp = fpx + float(y * scale)
                self.assertEqual(fpa, tmp)


    def testSubtraction(self):
        """subtraction operators should promote & anti-commute"""
        scale = 0.0625
        for x in range(-32, 16):
            fpx = FixedPoint.FPnum(x * scale)
            for y in range(-16, 32):
                fpy = FixedPoint.FPnum(y * scale)
                fpa = FixedPoint.FPnum((x - y) * scale)

                # compute various forms of a = (x - y):

                self.assertEqual(fpa, fpx - fpy)
                self.assertEqual(-fpa, fpy - fpx)
                self.assertEqual((x - y) * scale, float(fpx - fpy))

                tmp = FixedPoint.FPnum(fpx)
                tmp -= fpy
                self.assertEqual(fpa, tmp)

                tmp = float(x * scale) - fpy
                self.assertEqual(fpa, tmp)

                tmp = fpx - float(y * scale)
                self.assertEqual(fpa, tmp)


    def testMultiplication(self):
        """multiplication operators should promote & commute"""
        scale = 0.25
        scale2 = scale * scale
        for x in range(-16, 32):
            fpx = FixedPoint.FPnum(x * scale)
            for y in range(-32, 16):
                fpy = FixedPoint.FPnum(y * scale)
                fpa = FixedPoint.FPnum((x * y) * scale2)

                # compute various forms of a = (x * y):

                self.assertEqual(fpa, fpx * fpy)
                self.assertEqual(fpa, fpy * fpx)
                self.assertEqual((x * y) * scale2, float(fpx * fpy))

                tmp = FixedPoint.FPnum(fpx)
                tmp *= fpy
                self.assertEqual(fpa, tmp)

                tmp = float(x * scale) * fpy
                self.assertEqual(fpa, tmp)

                tmp = fpx * float(y * scale)
                self.assertEqual(fpa, tmp)


    def testDivision(self):
        """division operators should promote & inverse-commute"""
        scale = 0.125
        scale2 = scale * scale
        for a in range(-32, 32):
            if a == 0: continue
            fpa = FixedPoint.FPnum(a * scale)
            for y in range(-16, 16):
                if y == 0: continue
                fpy = FixedPoint.FPnum(y * scale)
                fpx = FixedPoint.FPnum((y * a) * scale2)

                # compute various forms of a = (x / y):

                self.assertAlmostEqual(fpa, fpx / fpy)
                self.assertAlmostEqual(1 / fpa, fpy / fpx)
                self.assertAlmostEqual((a * scale), float(fpx / fpy))

                tmp = FixedPoint.FPnum(fpx)
                tmp /= fpy
                self.assertAlmostEqual(fpa, tmp)

                tmp = float(a * y * scale2) / fpy
                self.assertAlmostEqual(fpa, tmp)

                tmp = fpx / float(y * scale)
                self.assertAlmostEqual(fpa, tmp)


if __name__ == "__main__":
    unittest.main()
