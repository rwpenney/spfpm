#!/usr/bin/python
# unit-tests for simple fixed-point Python module
# $Revision$, $Date$
# RW Penney, January 2006

import math, sys, unittest
sys.path.insert(0, '..')
from FixedPoint import FXnum, FXfamily, \
        FXoverflowError, FXdomainError, FXfamilyError


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
        if FXnum(0):
            self.fail()
        if FXnum(1):
            pass
        else:
            self.fail()


    def testImmutable(self):
        """arithmetic operations on object should not alter orignal value"""
        scale = 0.297
        for i in range(-8, 8):
            orig = FXnum(i * scale)

            x = FXnum(i * scale)
            x0 = x
            if x is x0:
                pass
            else:
                self.fail()

            x = FXnum(i * scale)
            x0 = x
            x += 1
            self.assertEqual(orig, x0)
            if x is x0: self.fail()

            x = FXnum(i * scale)
            x0 = x
            x -= 1
            self.assertEqual(orig, x0)
            if x is x0: self.fail()

            x = FXnum(i * scale)
            x0 = x
            x *= 2
            self.assertEqual(orig, x0)
            if x is x0: self.fail()

            x = FXnum(i * scale)
            x0 = x
            x /= 2
            self.assertEqual(orig, x0)
            if x is x0: self.fail()

    def testFamEquality(self):
        """check tests on equivalence of FXfamilies"""
        idxlist = [8, 16, 24, 33, 59]
        for idx in idxlist:
            fam0 = FXfamily(idx)
            for jdx in idxlist:
                fam1 = FXfamily(jdx)

                if idx == jdx:
                    self.failUnless(fam0 == fam1)
                    self.failIf(fam0 != fam1)
                else:
                    self.failIf(fam0 == fam1)
                    self.failUnless(fam0 != fam1)


    def testConversion(self):
        """check that conversion between families preserves values"""
        famlist = [FXfamily(b) for b in [32, 40, 48, 80, 120]]
        for i in range(1,10):
            xpos = (float)(1 << (2 * i)) + 1.0 / (1 << i);
            for x in [xpos, -xpos]:
               for fam0 in famlist:
                    fp0 = FXnum(x, fam0)
                    for fam1 in famlist:
                        fp1 = FXnum(fp0, fam1)
                        try: f = (fp0 == fp1)
                        except FXfamilyError:
                            self.failIf(fam0 is fam1)
                        else:
                            self.failUnless(fam0 is fam1)
                        self.assertAlmostEqual(x, float(fp0))
                        self.assertAlmostEqual(x, float(fp1))


    def testPrinting(self):
        """check conversion to string"""
        for i in range(1, 10):
            v = 2 ** i
            for x in [v, -v, 1.0/v, -1.0/v]:
                fpa = "%.8g" % x
                fpx = str(FXnum(x))
                self.assertEqual(fpa, fpx)

    def testRepresentation(self):
        """check repr() functionality"""
        for i in range(1, 30):
            v = 1.7 ** i
            for x in [v, -v, 1.0/v, -1.0/v]:
                fp0 = FXnum(x)
                # ensure that value extracted via repr() is in same FXfamily:
                fpb = FXnum(eval(repr(fp0)), family=fp0.family)
                self.assertEqual(fp0, fpb)

    def testIntCasts(self):
        """rounding on casting to int/long should match float-conversions"""
        for i in range(-40,40):
            x = i / 8.0
            self.assertEqual(int(x), int(FXnum(x)))
            self.assertEqual(long(x), long(FXnum(x)))


    def testNegating(self):
        """check prefix operators"""
        fam17 = FXfamily(17)
        for i in range(-32, 32):
            x = i * 0.819
            fx = FXnum(x, fam17)
            zero = FXnum(0, fam17)
            try:
                self.assertEqual(zero, fx + (-fx))
                self.assertEqual(zero, -fx + fx)
                self.assertEqual((-1 * fx), -fx)
                self.assertEqual(zero, (-1 * fx) + (-fx) + 2 * (+fx))
            except FXexception:
                self.fail()


    def testAddition(self):
        """addition operators should promote & commute"""
        scale = 0.125
        for x in range(-16, 16):
            fpx = FXnum(x * scale)
            for y in range(-32, 32):
                fpy = FXnum(y * scale)
                fpa = FXnum((x + y) * scale)

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
            fpx = FXnum(x * scale)
            for y in range(-16, 32):
                fpy = FXnum(y * scale)
                fpa = FXnum((x - y) * scale)

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
            fpx = FXnum(x * scale)
            for y in range(-32, 16):
                fpy = FXnum(y * scale)
                fpa = FXnum((x * y) * scale2)

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
        fam62 = FXfamily(62)
        scale = 0.125
        scale2 = scale * scale
        for a in range(-32, 32):
            if a == 0: continue
            fpa = FXnum(a * scale, fam62)
            for y in range(-16, 16):
                if y == 0: continue
                fpy = FXnum(y * scale, fam62)
                fpx = FXnum((y * a) * scale2, fam62)

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
        famlist = [FXfamily(res) for res in [8, 16, 40, 90]]
        for fam0 in famlist:
            for fam1 in famlist:
                x = FXnum(2, fam0)
                y = FXnum(3, fam1)
                try: a = x + y
                except FXfamilyError: self.failIf(fam0 is fam1)
                else: self.failUnless(fam0 is fam1)
                try: a = x - y
                except FXfamilyError: self.failIf(fam0 is fam1)
                else: self.failUnless(fam0 is fam1)
                try: a = x * y
                except FXfamilyError: self.failIf(fam0 is fam1)
                else: self.failUnless(fam0 is fam1)
                try: a = x / y
                except FXfamilyError: self.failIf(fam0 is fam1)
                else: self.failUnless(fam0 is fam1)

    def testIntRange(self):
        for top in [-4, -2, 0, 2, 4, 6]:
            fam = FXfamily(16, top)
            a = FXnum(1.0/16.01, fam)
            zero = FXnum(0, fam)
            limit = 1 << (top + 4)

            cnt, x, y = 0, zero, zero
            while cnt < (limit + 5):
                cnt += 1

                try: x += a
                except FXoverflowError:
                    if cnt <= limit: self.fail()
                else:
                    if cnt > limit: self.fail()

                try: y -= a
                except FXoverflowError:
                    if cnt <= limit: self.fail()
                else:
                    if cnt > limit: self.fail()

            try: x = zero + a * limit
            except FXoverflowError: self.fail()
            try: x = zero + a * (limit + 1)
            except FXoverflowError: pass
            else: self.fail()

            try: x = zero - a * limit
            except FXoverflowError: self.fail()
            try: x = zero - a * (limit + 1)
            except FXoverflowError: pass
            else: self.fail()

    def testSqrt(self):
        """sqrt method should find square-roots"""
        fam62 = FXfamily(62)
        scale = 0.94
        for i in range(-40, 40):
            x = i * scale
            fx = FXnum(x, fam62)
            try:
                rt = fx.sqrt()
            except FXdomainError:
                self.failIf(x >= 0)
            else:
                rt2 = float(rt * rt)
                self.assertAlmostEqual(x, rt2)
                if i == 0:
                    self.assertEqual(FXnum(0, fam62), rt)


    def testExp(self):
        """exponent method should agree with math.exp"""
        fam62 = FXfamily(62)
        scale = 0.23
        for i in range(-32, 32):
            x = i * scale
            exp_true = math.exp(x)
            exp = FXnum(x, fam62).exp()
            self.assertAlmostEqual(exp_true, exp)


    def testLog(self):
        """logarithm method agree with math.log"""
        fam62 = FXfamily(62)
        base = 1.5
        for i in range(1, 32):
            for j in range(0,2):
                if j == 0:
                    x = 1.0 / (base ** i)
                else:
                    x = base ** i
                log_true = math.log(x)
                log = FXnum(x, fam62).log()
                self.assertAlmostEqual(log_true, log)


    def testExpLog(self):
        """exp and log methods should be inverses & agree with math.*"""
        fam62 = FXfamily(62)
        scale = 0.27
        for i in range(-32, 32):
            x = i * scale
            exp = FXnum(x, fam62).exp()
            logexp = exp.log()
            self.assertAlmostEqual(x, float(logexp))


    def testPow(self):
        fam62 = FXfamily(62)
        scale = 0.205
        scale2 = 0.382
        for i in range(1, 32):
            x = i * scale
            pow = FXnum(0, fam62) ** x
            self.assertEqual(FXnum(1, fam62), pow)
            for j in range(-16, 16):
                y = j * scale2
                pow_true = math.pow(x, y)
                pow = FXnum(x, fam62) ** y
                self.assertAlmostEqual(pow_true, pow)


    def testSinCos(self):
        """sin/cos methods agree with math.sin/cos"""
        fam62 = FXfamily(62)
        scale = 0.342
        fang = FXnum(0, fam62)
        self.assertEqual(fang, fang.sin())
        self.assertEqual(FXnum(1,fam62), fang.cos())
        for i in range(-32, 32):
            x = i * scale
            sin_true = math.sin(x)
            cos_true = math.cos(x)
            fang = FXnum(x, fam62)
            (sin, cos) = fang.sincos()
            self.assertAlmostEqual(sin_true, sin)
            self.assertAlmostEqual(cos_true, cos)
            self.assertEqual(sin, fang.sin())
            self.assertEqual(cos, fang.cos())


    def testArctan(self):
        """atan method agree with math.sin/cos"""
        fam62 = FXfamily(62)
        scale = 0.277
        for i in range(-32, 32):
            tan = i * scale
            ang_true = math.atan(tan)
            ang = FXnum(tan, fam62).atan()
            self.assertAlmostEqual(ang_true, ang)


    def testArcSinCos(self):
        """asin/acos methods should be inverses of sin/cos"""
        fam62 = FXfamily(62)
        trig = FXnum(0, fam62)
        self.assertEqual(trig, trig.asin())
        self.assertEqual(trig, FXnum(1,fam62).acos())
        steps = 20
        for i in range(0, steps + 1):
            for s in [-1.0, 1.0]:
                trig = FXnum((i * s) / steps, fam62)
                isn = trig.asin()
                self.failUnless(abs(isn) <= fam62.GetPi() / 2)
                self.assertAlmostEqual(float(trig), float(isn.sin()))
                ics = trig.acos()
                self.failUnless(0 <= ics and ics <= fam62.GetPi())
                self.assertAlmostEqual(float(trig), float(ics.cos()))


# ensure support for older unittest module (e.g. Python-2.2)
try:
    fn = FixedPointTest.assertAlmostEqual
except AttributeError:
    def almostequal(obj, first, second, places=7):
        obj.failUnless(abs(first-second) < (10.0 ** -places))
    FixedPointTest.assertAlmostEqual = almostequal


if __name__ == "__main__":
    unittest.main()

# vim: set ts=4 sw=4 et:
