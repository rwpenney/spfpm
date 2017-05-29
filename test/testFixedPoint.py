#!/usr/bin/python3
# Unit-tests for simple Python fixed-point module (spfpm)
# RW Penney, January 2006

import math, sys, unittest
sys.path.insert(0, '..')
from FixedPoint import FXfamily, FXnum, \
        FXoverflowError, FXdomainError, FXfamilyError


class FixedPointTest(unittest.TestCase):
    def assertAlmostEqual(self, first, second, places=7):
        """Overload TestCase.assertAlmostEqual() to avoid use of round()"""
        tol = 10.0 ** -places
        self.assertTrue(abs(first-second) < tol,
                        '{} and {} differ by more than {} ({})'.format(
                            first, second, tol, (first - second)))


class TestFamilies(FixedPointTest):
    def testFamEquality(self):
        """Check tests on equivalence of FXfamilies"""
        idxlist = [8, 16, 24, 33, 59]
        for idx in idxlist:
            fam0 = FXfamily(idx)
            for jdx in idxlist:
                fam1 = FXfamily(jdx)

                if idx == jdx:
                    self.assertTrue(fam0 == fam1)
                    self.assertFalse(fam0 != fam1)
                else:
                    self.assertFalse(fam0 == fam1)
                    self.assertTrue(fam0 != fam1)

    def testFamilyProtection(self):
        """Check that arithmetic operators do not transmute resolution families"""
        famlist = [FXfamily(res) for res in [8, 16, 40, 90]]
        for fam0 in famlist:
            for fam1 in famlist:
                x = FXnum(2, fam0)
                y = FXnum(3, fam1)
                try: a = x + y
                except FXfamilyError: self.assertFalse(fam0 is fam1)
                else: self.assertTrue(fam0 is fam1)
                try: a = x - y
                except FXfamilyError: self.assertFalse(fam0 is fam1)
                else: self.assertTrue(fam0 is fam1)
                try: a = x * y
                except FXfamilyError: self.assertFalse(fam0 is fam1)
                else: self.assertTrue(fam0 is fam1)
                try: a = x / y
                except FXfamilyError: self.assertFalse(fam0 is fam1)
                else: self.assertTrue(fam0 is fam1)

    def testMathConsts(self):
        """Check various mathematical constants against math module."""
        for ident, target in [('unity', 1.0),
                              ('exp1',  math.e),
                              ('log2',  math.log(2)),
                              ('pi',    math.pi),
                              ('sqrt2', math.sqrt(2))]:
            self.assertAlmostEqual(getattr(FXfamily(64), ident),
                                   target, places=15)

    def testConstPrecision(self):
        """Check claimed precision of constants such as pi, log2, etc."""

        extra_bits = 64
        for res in (8, 16, 32, 64, 256, 1024):
            fam0 = FXfamily(res)
            fam_extra = FXfamily(res + extra_bits)

            for field in ('exp1', 'log2', 'pi', 'sqrt2'):
                x0 = getattr(fam0, field).scaledval
                x_extra = getattr(fam_extra, field).scaledval

                self.assertEqual(x0, x_extra >> extra_bits)

    def testIntRange(self):
        """Check detection of overflow of integer part."""
        for top in [-3, -2, 0, 2, 4, 6]:
            fam = FXfamily(16, top)
            a = FXnum(1.0/16.01, fam)
            zero = FXnum(0, fam)
            limit = 1 << (top + 4 - 1)  # Unlikely to be valid FXnum(,fam)

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


class TestNumInit(FixedPointTest):
    def testRawBuild(self):
        """Check equivalence of FXnum._rawbuild() and FXnum()."""
        fam = FXfamily(10, 5)
        x = FXnum(val=9.7531, family=fam)
        xraw = FXnum._rawbuild(fam, x.scaledval)
        self.assertEqual(x, xraw)
        self.assertIsInstance(x, FXnum)
        self.assertIsInstance(xraw, FXnum)
        self.assertIsNot(x, xraw)

    def testLongRounding(self):
        """Check assumptions about integers rounding towards minus infinity."""
        for base in range(2, 8):
            for step in range(1, 5):
                for inc in range(1, base):
                    pos = int((base * step) + inc)
                    self.assertEqual(int(step), (pos // base))
                    neg = int((base * -step) - inc)
                    self.assertEqual(int(-step - 1), (neg // base))


class TestNumConvert(FixedPointTest):
    def testBoolConditions(self):
        """Values used in boolean expressions should behave as true/false"""
        if FXnum(0):
            self.fail()
        if FXnum(1):
            pass
        else:
            self.fail()

    def testIntCasts(self):
        """Rounding on casting to int should match float-conversions"""
        for i in range(-40,40):
            x = i / 8.0
            self.assertEqual(int(x), int(FXnum(x)))

    def testNegating(self):
        """Check prefix operators"""
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

    def testFamilyConversion(self):
        """Check that conversion between families preserves values"""
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
                            self.assertFalse(fam0 is fam1)
                        else:
                            self.assertTrue(fam0 is fam1)
                        self.assertAlmostEqual(x, float(fp0))
                        self.assertAlmostEqual(x, float(fp1))



class TestNumPrint(FixedPointTest):
    def testPrinting(self):
        """Check conversion to string"""
        for i in range(1, 10):
            v = 2 ** i
            for x in [v, -v, 1.0/v, -1.0/v]:
                fpa = "%.8g" % x
                fpx = str(FXnum(x))
                self.assertEqual(fpa, fpx)

    def testRepresentation(self):
        """Check repr() functionality"""
        for i in range(1, 30):
            v = 1.7 ** i
            for x in [v, -v, 1.0/v, -1.0/v]:
                fp0 = FXnum(x)
                # ensure that value extracted via repr() is in same FXfamily:
                fpb = FXnum(eval(repr(fp0)), family=fp0.family)
                self.assertEqual(fp0, fpb)


class TestArithmetic(FixedPointTest):
    def testAddition(self):
        """Addition operators should promote & commute"""
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
        """Subtraction operators should promote & anti-commute"""
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
        """Multiplication operators should promote & commute"""
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
        """Division operators should promote & inverse-commute"""
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

    def testBitShifts(self):
        """Check effects of left & right shift operators."""
        fam = FXfamily(32)

        self.assertEqual(FXnum(1, fam) << 2, 4)
        self.assertEqual(FXnum(3, fam) << 4, 48)
        self.assertEqual(FXnum(-7, fam) << 8, -7 * 256)

        self.assertEqual(FXnum(1, fam) >> 1, 0.5)
        self.assertEqual(FXnum(12, fam) >> 2, 3)
        self.assertEqual(FXnum(-71 * 1024, fam) >> 12, -17.75)

    def testImmutable(self):
        """Arithmetic operations on object should not alter orignal value"""
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


class TestPowers(FixedPointTest):
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
                self.assertFalse(x >= 0)
            else:
                rt2 = float(rt * rt)
                self.assertAlmostEqual(x, rt2)
                if i == 0:
                    self.assertEqual(FXnum(0, fam62), rt)

    def testPow(self):
        """Check raising FXnums to powers."""
        fam62 = FXfamily(62)
        scale = 0.205
        scale2 = 0.382
        for i in range(1, 32):
            x = i * scale

            pwr = FXnum(0, fam62) ** x
            self.assertEqual(FXnum(1, fam62), pwr)

            for j in range(-16, 16):
                y = j * scale2
                pwr_true = math.pow(x, y)
                pwr = FXnum(x, fam62) ** y
                self.assertAlmostEqual(pwr_true, pwr)


class TestExpLog(FixedPointTest):
    def testExp(self):
        """Exponent method should agree with math.exp"""
        fam62 = FXfamily(62)
        scale = 0.23
        for i in range(-32, 32):
            x = i * scale
            exp_true = math.exp(x)
            exp = FXnum(x, fam62).exp()
            self.assertAlmostEqual(exp_true, exp)

    def testLog(self):
        """Logarithm method agree with math.log"""
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


class TestTrig(FixedPointTest):
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

        self.assertEqual(FXnum(0, fam62), 0)

        for i in range(-32, 32):
            tan = i * scale
            ang_true = math.atan(tan)
            ang = FXnum(tan, fam62).atan()
            self.assertAlmostEqual(ang_true, ang)
            self.assertAlmostEqual(float(ang.tan()), tan)

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
                self.assertTrue(abs(isn) <= fam62.pi / 2)
                self.assertAlmostEqual(float(trig), float(isn.sin()))
                self.assertAlmostEqual(float(isn), math.asin(float(trig)))

                ics = trig.acos()
                self.assertTrue(0 <= ics and ics <= fam62.pi)
                self.assertAlmostEqual(float(trig), float(ics.cos()))
                self.assertAlmostEqual(float(ics), math.acos(float(trig)))


if __name__ == "__main__":
    unittest.main()

# vim: set ts=4 sw=4 et:
