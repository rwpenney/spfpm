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
                    self.assertEqual(long(step), (pos // base))
                    neg = long((base * -step) - inc)
                    self.assertEqual(long(-step - 1), (neg // base))


    def testBoolConditions(self):
        """values used in boolean expressions should behave as true/false"""
        if FixedPoint.FXnum(0):
            self.fail()
        if FixedPoint.FXnum(1):
            pass
        else:
            self.fail()


    def testImmutable(self):
        """arithmetic operations on object should not alter orignal value"""
        scale = 0.297
        for i in range(-8, 8):
            orig = FixedPoint.FXnum(i * scale)

            x = FixedPoint.FXnum(i * scale)
            x0 = x
            if x is x0:
                pass
            else:
                self.fail()

            x = FixedPoint.FXnum(i * scale)
            x0 = x
            x += 1
            self.assertEqual(orig, x0)
            if x is x0: self.fail()

            x = FixedPoint.FXnum(i * scale)
            x0 = x
            x -= 1
            self.assertEqual(orig, x0)
            if x is x0: self.fail()

            x = FixedPoint.FXnum(i * scale)
            x0 = x
            x *= 2
            self.assertEqual(orig, x0)
            if x is x0: self.fail()

            x = FixedPoint.FXnum(i * scale)
            x0 = x
            x /= 2
            self.assertEqual(orig, x0)
            if x is x0: self.fail()


    def testConversion(self):
        """check that conversion between families preserves values"""
        famlist = [FixedPoint.FXfamily(b) for b in [32, 40, 48, 80, 120]]
        for i in range(1,10):
            xpos = (float)(1 << (2 * i)) + 1.0 / (1 << i);
            for x in [xpos, -xpos]:
               for fam0 in famlist:
                    fp0 = FixedPoint.FXnum(x, fam0)
                    for fam1 in famlist:
                        fp1 = FixedPoint.FXnum(fp0, fam1)
                        try: f = (fp0 == fp1)
                        except FixedPoint.FXfamilyError:
                            self.failIf(fam0 is fam1)
                        else:
                            self.failUnless(fam0 is fam1)
                        self.assertAlmostEqual(x, float(fp0))
                        self.assertAlmostEqual(x, float(fp1))


    def testPrinting(self):
        """check conversion to string"""
        for i in range(1,10):
            v = 2 ** i
            for x in [v, 1.0/v]:
                fpa = "%.8g" % x
                fpx = str(FixedPoint.FXnum(x))
                self.assertEqual(fpa, fpx)


    def testIntCasts(self):
        """rounding on casting to int/long should match float-conversions"""
        for i in range(-40,40):
            x = i / 8.0
            self.assertEqual(int(x), int(FixedPoint.FXnum(x)))
            self.assertEqual(long(x), long(FixedPoint.FXnum(x)))


    def testNegating(self):
        """check prefix operators"""
        fam17 = FixedPoint.FXfamily(17)
        for i in range(-32, 32):
            x = i * 0.819
            fx = FixedPoint.FXnum(x, fam17)
            zero = FixedPoint.FXnum(0, fam17)
            try:
                self.assertEqual(zero, fx + (-fx))
                self.assertEqual(zero, -fx + fx)
                self.assertEqual((-1 * fx), -fx)
                self.assertEqual(zero, (-1 * fx) + (-fx) + 2 * (+fx))
            except FixedPoint.FXexception:
                self.fail()


    def testAddition(self):
        """addition operators should promote & commute"""
        scale = 0.125
        for x in range(-16, 16):
            fpx = FixedPoint.FXnum(x * scale)
            for y in range(-32, 32):
                fpy = FixedPoint.FXnum(y * scale)
                fpa = FixedPoint.FXnum((x + y) * scale)

                # compute various forms of a = (x + y):

                self.assertEqual(fpa, fpx + fpy)
                self.assertEqual(fpa, fpy + fpx)
                self.assertEqual((x + y) * scale, float(fpx + fpy))

                tmp = fpx
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
            fpx = FixedPoint.FXnum(x * scale)
            for y in range(-16, 32):
                fpy = FixedPoint.FXnum(y * scale)
                fpa = FixedPoint.FXnum((x - y) * scale)

                # compute various forms of a = (x - y):

                self.assertEqual(fpa, fpx - fpy)
                self.assertEqual(-fpa, fpy - fpx)
                self.assertEqual((x - y) * scale, float(fpx - fpy))

                tmp = fpx
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
            fpx = FixedPoint.FXnum(x * scale)
            for y in range(-32, 16):
                fpy = FixedPoint.FXnum(y * scale)
                fpa = FixedPoint.FXnum((x * y) * scale2)

                # compute various forms of a = (x * y):

                self.assertEqual(fpa, fpx * fpy)
                self.assertEqual(fpa, fpy * fpx)
                self.assertEqual((x * y) * scale2, float(fpx * fpy))

                tmp = fpx
                tmp *= fpy
                self.assertEqual(fpa, tmp)

                tmp = float(x * scale) * fpy
                self.assertEqual(fpa, tmp)

                tmp = fpx * float(y * scale)
                self.assertEqual(fpa, tmp)


    def testDivision(self):
        """division operators should promote & inverse-commute"""
        fam62 = FixedPoint.FXfamily(62)
        scale = 0.125
        scale2 = scale * scale
        for a in range(-32, 32):
            if a == 0: continue
            fpa = FixedPoint.FXnum(a * scale, fam62)
            for y in range(-16, 16):
                if y == 0: continue
                fpy = FixedPoint.FXnum(y * scale, fam62)
                fpx = FixedPoint.FXnum((y * a) * scale2, fam62)

                # compute various forms of a = (x / y):

                self.assertAlmostEqual(fpa, fpx / fpy)
                self.assertAlmostEqual(1 / fpa, fpy / fpx)
                self.assertAlmostEqual((a * scale), float(fpx / fpy))

                tmp = fpx
                tmp /= fpy
                self.assertAlmostEqual(fpa, tmp)

                tmp = float(a * y * scale2) / fpy
                self.assertAlmostEqual(fpa, tmp)

                tmp = fpx / float(y * scale)
                self.assertAlmostEqual(fpa, tmp)


    def testFamilyProtection(self):
        """check that arithmetic operators do not transmute resolution families"""
        famlist = [FixedPoint.FXfamily(res) for res in [8, 16, 40, 90]]
        for fam0 in famlist:
            for fam1 in famlist:
                x = FixedPoint.FXnum(2, fam0)
                y = FixedPoint.FXnum(3, fam1)
                try: a = x + y
                except FixedPoint.FXfamilyError: self.failIf(fam0 is fam1)
                else: self.failUnless(fam0 is fam1)
                try: a = x - y
                except FixedPoint.FXfamilyError: self.failIf(fam0 is fam1)
                else: self.failUnless(fam0 is fam1)
                try: a = x * y
                except FixedPoint.FXfamilyError: self.failIf(fam0 is fam1)
                else: self.failUnless(fam0 is fam1)
                try: a = x / y
                except FixedPoint.FXfamilyError: self.failIf(fam0 is fam1)
                else: self.failUnless(fam0 is fam1)


    def testSqrt(self):
        """sqrt method should find square-roots"""
        fam62 = FixedPoint.FXfamily(62)
        scale = 0.94
        for i in range(-40, 40):
            x = i * scale
            fx = FixedPoint.FXnum(x, fam62)
            try:
                rt = fx.sqrt()
            except FixedPoint.FXdomainError:
                self.failIf(x >= 0)
            else:
                rt2 = float(rt * rt)
                self.assertAlmostEqual(x, rt2)
                if i == 0:
                    self.assertEqual(FixedPoint.FXnum(0, fam62), rt)


    def testExp(self):
        """exponent method should agree with math.exp"""
        fam62 = FixedPoint.FXfamily(62)
        scale = 0.23
        for i in range(-32, 32):
            x = i * scale
            exp_true = math.exp(x)
            exp = FixedPoint.FXnum(x, fam62).exp()
            self.assertAlmostEqual(exp_true, exp)


    def testLog(self):
        """logarithm method agree with math.log"""
        fam62 = FixedPoint.FXfamily(62)
        base = 1.5
        for i in range(1, 32):
            for j in range(0,2):
                if j == 0:
                    x = 1.0 / (base ** i)
                else:
                    x = base ** i
                log_true = math.log(x)
                log = FixedPoint.FXnum(x, fam62).log()
                self.assertAlmostEqual(log_true, log)


    def testExpLog(self):
        """exp and log methods should be inverses & agree with math.*"""
        fam62 = FixedPoint.FXfamily(62)
        scale = 0.27
        for i in range(-32, 32):
            x = i * scale
            exp = FixedPoint.FXnum(x, fam62).exp()
            logexp = exp.log()
            self.assertAlmostEqual(x, float(logexp))


    def testPow(self):
        fam62 = FixedPoint.FXfamily(62)
        scale = 0.205
        scale2 = 0.382
        for i in range(1, 32):
            x = i * scale
            pow = FixedPoint.FXnum(0, fam62) ** x
            self.assertEqual(FixedPoint.FXnum(1, fam62), pow)
            for j in range(-16, 16):
                y = j * scale2
                pow_true = math.pow(x, y)
                pow = FixedPoint.FXnum(x, fam62) ** y
                self.assertAlmostEqual(pow_true, pow)


    def testSinCos(self):
        """sin/cos methods agree with math.sin/cos"""
        fam62 = FixedPoint.FXfamily(62)
        scale = 0.342
	fang = FixedPoint.FXnum(0, fam62)
	self.assertEqual(fang, fang.sin())
	self.assertEqual(FixedPoint.FXnum(1,fam62), fang.cos())
        for i in range(-32, 32):
            x = i * scale
            sin_true = math.sin(x)
            cos_true = math.cos(x)
            fang = FixedPoint.FXnum(x, fam62)
            (sin, cos) = fang.sincos()
            self.assertAlmostEqual(sin_true, sin)
            self.assertAlmostEqual(cos_true, cos)
            self.assertEqual(sin, fang.sin())
            self.assertEqual(cos, fang.cos())


    def testArctan(self):
        """atan method agree with math.sin/cos"""
        fam62 = FixedPoint.FXfamily(62)
        scale = 0.277
        for i in range(-32, 32):
            tan = i * scale
            ang_true = math.atan(tan)
            ang = FixedPoint.FXnum(tan, fam62).atan()
            self.assertAlmostEqual(ang_true, ang)


    def testArcSinCos(self):
        """asin/acos methods should be inverses of sin/cos"""
        fam62 = FixedPoint.FXfamily(62)
        steps = 20
        for i in range(0, steps + 1):
            for s in [-1.0, 1.0]:
                trig = FixedPoint.FXnum((i * s) / steps, fam62)
                isn = trig.asin()
                self.failUnless(abs(isn) <= fam62.GetPi() / 2)
                self.assertAlmostEqual(float(trig), float(isn.sin()))
                ics = trig.acos()
                self.failUnless(0 <= ics and ics <= fam62.GetPi())
                self.assertAlmostEqual(float(trig), float(ics.cos()))



if __name__ == "__main__":
    unittest.main()
