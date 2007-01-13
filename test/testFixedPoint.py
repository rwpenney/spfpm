#!/usr/bin/python
# unit-tests for simple fixed-point Python module
# $Revision$, $Date$
# RW Penney, January 2006

import math, sys, unittest
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


    def testExp(self):
        """exponent method agree with math.exp"""
        scale = 0.23
        for i in range(-32, 32):
            x = i * scale
            exp_true = math.exp(x)
            exp = FixedPoint.FPnum(x).exp()
            self.assertAlmostEqual(exp_true, exp)


    def testLog(self):
        """logarithm method agree with math.log"""
        """exp and log methods should be inverses & agree with math.*"""
        base = 1.5
        for i in range(1, 32):
            for j in range(0,2):
                if j == 0:
                    x = 1 / (base ** i)
                else:
                    x = base ** i
                log_true = math.log(x)
                log = FixedPoint.FPnum(x).log()
                self.assertAlmostEqual(log_true, log)


    def testExpLog(self):
        """exp and log methods should be inverses & agree with math.*"""
        scale = 0.27
        for i in range(-32, 32):
            x = i * scale
            exp = FixedPoint.FPnum(x).exp()
            logexp = exp.log()
            self.assertAlmostEqual(x, float(logexp))


    def testPow(self):
        scale = 0.205
        scale2 = 0.382
        for i in range(1, 32):
            x = i * scale
            pow = FixedPoint.FPnum(0) ** x
            self.assertEqual(FixedPoint.FPnum(1), pow)
            for j in range(-16, 16):
                y = j * scale2
                pow_true = math.pow(x, y)
                pow = FixedPoint.FPnum(x) ** y
                self.assertAlmostEqual(pow_true, pow)


    def testSinCos(self):
        """sin/cos methods agree with math.sin/cos"""
        scale = 0.342
        for i in range(-32, 32):
            x = i * scale
            sin_true = math.sin(x)
            cos_true = math.cos(x)
            (sin, cos) = FixedPoint.FPnum(x).sincos()
            self.assertAlmostEqual(sin_true, sin)
            self.assertAlmostEqual(cos_true, cos)



if __name__ == "__main__":
    unittest.main()
