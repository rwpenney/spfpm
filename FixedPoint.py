#!/usr/bin/python
# Simple Python Fixed-Point Module (SPFPM)
# $Revision$, $Date$
# Copyright 2006-2007, RW Penney


# This file is Copyright 2006-2007, RW Penney
# and is released under the Python-2.4.2 license
# (see http://www.python.org/psf/license),
# it therefore comes with NO WARRANTY, and NO CLAIMS OF FITNESS FOR ANY PURPOSE.
# However, the author welcomes *constructive* feedback
# and bug-fixes via: rwpenney 'AT' users 'DOT' sourceforge 'DOT' net


"""Simple fixed-point numerical class

Creation:
    x = FXnum(2)
    y = FXnum(1.2, FXfamily(n_bits=108))

Manipulation:
    x *= 2
    rt = x.sqrt()

Output:
    print x, rt
    q = float(x)

Note:
    Be careful not to assume that a large number of fractional bits within
    a number will necessarily mean large accuracy. For example, computations
    involving exponentiation and logarithms are intrinsically vulnerable to
    magnifying mere rounding errors in their inputs into significant errors
    in their outputs. This is a fact of life with any approximation to
    real arithmetic using finite-precision quantities.
"""

class FXfamily(object):
    def __init__(self, n_bits=64):
        self.fraction_bits = n_bits         # bits to right of binary point
        self.scale = 1L << n_bits
        self.round = 1L << (n_bits - 1)
        self.exp1 = None                    # cache of exp(1)
        self.log2 = None                    # cache of log(2)
        self.Pi = None                      # cache of 3.14159...

    def __repr__(self):
        return 'FXfamily(%d)' % (self.fraction_bits)

    def __eq__(self, other):
        if isinstance(other, FXfamily):
            return self.fraction_bits == other.fraction_bits
        else:
            return false

    def __ne__(self, other):
        if isinstance(other, FXfamily):
            return self.fraction_bits != other.fraction_bits
        else:
            return true

    def GetResolution(self):
        return self.fraction_bits

    def GetExp1(self):
        """return cached value of exp(1)"""
        if self.exp1 is None:
            # bute-force calculation of exp(1) using augmented accuracy:
            augfamily = FXfamily(self.fraction_bits + 8)
            augexp = FXnum(1, augfamily)._rawexp()
            self.exp1 = FXnum(augexp, self)
        return self.exp1

    def GetLog2(self):
        """return cached value of log(2)"""
        if self.log2 is None:
            # bute-force calculation of log(2) using augmented accuracy:
            augfamily = FXfamily(self.fraction_bits + 8)
            auglog2 = FXnum(2, augfamily)._rawlog()
            self.log2 = FXnum(auglog2, self)
        return self.log2

    def GetPi(self):
        """return cached value of pi"""
        if self.Pi is None:
            # bute-force calculation of 8*atan(pi/8) using augmented accuracy:
            augfamily = FXfamily(self.fraction_bits + 8)
            rt2 = FXnum(2, augfamily).sqrt()
            tan8 = (rt2 - 1)
            augpi = 8 * tan8._rawarctan()
            self.Pi = FXnum(augpi, self)
        return self.Pi

    def Convert(self, other, other_val):
        """convert number from different number of fraction-bits"""
        bit_inc = self.fraction_bits - other.fraction_bits
        if bit_inc == 0:
            return other_val
        elif bit_inc > 0:
            new_val = other_val << bit_inc
            if other_val > 0:
                new_val |= 1L << (bit_inc - 1)
            else:
                new_val |= ((1L << (bit_inc -1)) - 1)
            return new_val
        else:
            return (other_val >> -bit_inc)
# ^^^ class FXfamily ^^^

_defaultFamily = FXfamily()



class FXexception(TypeError):
    """Signal that family-types of FXnums in binary operation are mismatched"""



class FXnum(object):
    def __init__(self, val=0L, family=_defaultFamily):
        assert isinstance(family, FXfamily)
        self.family = family
        if isinstance(val, FXnum):
            self.scaledval = family.Convert(val.family, val.scaledval)
        elif isinstance(val, list):
            sval = val[0]
            self.scaledval = sval
        else:
            self.scaledval = long(val * family.scale)

    def __repr__(self):
        return 'FXnum([%d], %s)' % (self.scaledval, self.family.__repr__())

    # converstion operations:
    def __int__(self):
        """Cast to (plain) integer"""
        return int((self.scaledval + self.family.round) / self.family.scale)

    def __long__(self):
        """Cast to long integer"""
        return long((self.scaledval + self.family.round) / self.family.scale)

    def __float__(self):
        """Cast to floating-point"""
        return float(self.scaledval) / float(self.family.scale)

    def _CastOrFail_(self, other):
        """turn number into FXnum or check that it is in same family"""
        if isinstance(other, FXnum):
            # binary operations must involve members of same family
            if not self.family is other.family:
                raise FXexception, 1
        else:
            # automatic casting from types other than FXnum is allowed:
            other = FXnum(other, self.family)
        return other

    # unary arithmetic operations:
    def __neg__(self):
        """Change sign"""
        new = FXnum()
        new.scaledval = -self.scaledval
        return new

    # arithmetic comparison tests:
    def __eq__(self, other):
        """Equality test"""
        other = self._CastOrFail_(other)
        return self.scaledval == other.scaledval and self.family == other.family

    def __ne__(self, other):
        """Inequality test"""
        other = self._CastOrFail_(other)
        return self.scaledval != other.scaledval

    def __ge__(self, other):
        """Greater-or-equal test"""
        other = self._CastOrFail_(other)
        return self.scaledval >= other.scaledval

    def __gt__(self, other):
        """Greater-than test"""
        other = self._CastOrFail_(other)
        return self.scaledval > other.scaledval

    def __le__(self, other):
        """Less-or-equal test"""
        other = self._CastOrFail_(other)
        return self.scaledval <= other.scaledval

    def __lt__(self, other):
        """Greater-than test"""
        other = self._CastOrFail_(other)
        return self.scaledval < other.scaledval

    def __nonzero__(self):
        """Test for non-zero"""
        return (self.scaledval != 0)

    # arithmetic combinations:
    def __add__(self, other):
        """Add another number"""
        other = self._CastOrFail_(other)
        new = FXnum(family=self.family)
        new.scaledval = self.scaledval + other.scaledval
        return new

    def __radd__(self, other):
        return FXnum(other, self.family) + self

    def __sub__(self, other):
        """Subtract another number"""
        other = self._CastOrFail_(other)
        new = FXnum(family=self.family)
        new.scaledval = self.scaledval - other.scaledval
        return new

    def __rsub__(self, other):
        return FXnum(other, self.family) - self

    def __mul__(self, other):
        """Multiply by another number"""
        other = self._CastOrFail_(other)
        new = FXnum(family=self.family)
        new.scaledval = (self.scaledval * other.scaledval + self.family.round) / self.family.scale
        return new

    def __rmul__(self, other):
        return FXnum(other, self.family) * self

    def __div__(self, other):
        """Divide by another number"""
        other = self._CastOrFail_(other)
        new = FXnum(family=self.family)
        new.scaledval = (self.scaledval * self.family.scale + self.family.round) / other.scaledval
        return new

    def __rdiv__(self, other):
        return FXnum(other, self.family) / self

    # printing/converstion routines:
    def __str__(self):
        """Convert number (as decimal) into string"""
        val = self.scaledval
        rep = ''
        if self.scaledval < 0:
            rep = '-'
            val *= -1
        whole = val / self.family.scale
        frac = val - self.family.scale * whole
        rep += str(whole)
        if frac != 0:
            rep += '.'
            idx = 0
            while idx < (self.family.fraction_bits / 3) and frac != 0:
                frac *= 10L
                q = frac / self.family.scale
                rep += str(q)
                frac -= q * self.family.scale
                idx += 1
        return rep

    # mathematical functions:
    def __pow__(self, other, modulus=None):
        assert modulus is None
        if self == 0:
            return FXnum(1, self.family)
        if isinstance(other, int) or isinstance(other, long):
            ipwr = other
            frac = FXnum(1, self.family)
        else:
            ipwr = long(other)
            frac = ((other - ipwr) * self.log()).exp()
        return self.intpower(ipwr) * frac

    def intpower(self, pwr):
        """compute integer power by repeated squaring"""
        assert isinstance(pwr, int) or isinstance(pwr, long)
        invert = False
        if pwr < 0:
            pwr *= -1
            invert = True
        result = FXnum(1, self.family)
        term = self
        while pwr != 0:
            if pwr & 1:
                result *= term
            pwr >>= 1
            term *= term
        if invert:
            result = FXnum(1, self.family) / result
        return result

    def sqrt(self):
        """Compute square-root of given number"""
        # calculate crude initial approximation:
        assert self.scaledval >= 0
        rt = FXnum(family=self.family)
        rt.scaledval = 1L << (self.family.fraction_bits / 2)
        val = self.scaledval
        while val > 0:
            val >>= 2
            rt.scaledval <<= 1
        # refine approximation by Newton iteration:
        while True:
            delta = (rt - self / rt) / 2
            rt -= delta
            if delta.scaledval == 0: break
        return rt

    def exp(self):
        """Compute exponential of given number"""
        pwr = long(self)
        return (self - pwr)._rawexp() * (self.family.GetExp1() ** pwr)

    def _rawexp(self):
        """Brute-force exponential of given number (assumed smallish)"""
        ex = FXnum(1, self.family)
        term = FXnum(1, self.family)
        idx = FXnum(1, self.family)
        while True:
            term *= self / idx
            ex += term
            idx += FXnum(1, self.family)
            if term.scaledval == 0: break
        return ex

    def log(self):
        """Compute (natural) logarithm of given number"""
        thresh = FXnum(2, self.family)
        assert self.scaledval > 0
        count = 0
        val = self
        while val > thresh:
            val /= 2
            count += 1
        while val < 1 / thresh:
            val *= 2
            count -= 1
        return val._rawlog() + count * self.family.GetLog2()

    def _rawlog(self):
        """Compute (natural) logarithm of given number (assumed close to 1)"""
        lg = FXnum(0, self.family)
        z = (self - 1) / (self + 1)
        z2 = z * z
        term = 2 * z
        idx = 1
        while True:
            lg += term / idx
            term *= z2
            idx += 2
            if term.scaledval == 0: break
        return lg

    def sincos(self):
        """Compute sine & cosine of given number (as angle in radians)"""
        reflect = False
        ang = self
        if ang < 0:
            ang *= -1
            reflect = True
        # find nearest multiple of pi/2:
        halfpi = self.family.GetPi() / 2
        idx = int(ang / halfpi + 0.5)
        # compute sin/cos of offset from nearest pi/2
        ang -= idx * halfpi
        (osn, ocs) = ang._rawsincos()
        # transform according to sin(ang+offset), cos(ang+offset):
        idx = idx % 4
        if idx == 0:
            (sn, cs) = (osn, ocs)
        elif idx == 1:
            (sn, cs) = (ocs, -osn)
        elif idx == 2:
            (sn, cs) = (-osn, -ocs)
        elif idx == 3:
            (sn, cs) = (-ocs, osn)
        else:
            raise FXexception
        if reflect:
            sn *= -1
        return (sn, cs)

    def _rawsincos(self):
        """Brute-force calculation of sine & cosine"""
        sn = FXnum(0, self.family)
        cs = FXnum(1, self.family)
        term = FXnum(1, self.family)
        idx = 1
        while (True):
            term *= self / idx
            if (idx % 2) == 0:
                if (idx % 4) == 0:
                    cs += term
                else:
                    cs -= term
            else:
                if (idx % 4) == 1:
                    sn += term
                else:
                    sn -= term
            idx += 1
            if term.scaledval == 0: break
        return (sn, cs)

    def arctan(self):
        """Compute inverse-tangent of given number (as angle in radians)"""
        reflect = False
        recip = False
        double = False
        tan = self
        if tan < 0:
            tan *= -1
            reflect = True
        if tan > 1:
            tan = 1 / tan
            recip = True
        if tan > 0.414:
            tan = ((1 + tan * tan).sqrt() - 1) / tan
            double = True
        ang = tan._rawarctan()
        if double:
            ang *= 2
        if recip:
            ang = self.family.GetPi() / 2 - ang
        if reflect:
            ang *= -1
        return ang

    def _rawarctan(self):
        """Brute-force inverse-tangent of given number (for |self|<1)"""
        atn = 1
        x2 = self * self
        omx2 = 1 - x2
        opx2 = 1 + x2
        x4 = x2 * x2
        term = x2
        idx = 1
        while True:
            delta = term * (4 * idx * omx2 + opx2) / (16 * idx * idx - 1)
            atn -= delta
            term *= x4
            idx += 1
            if delta.scaledval == 0: break
        return self * atn
# ^^^ class FXnum ^^^


class FPnum(FXnum):
    """Backwards-compatibility class following name-change from FPnum to FXnum.
    The name-change was prompted in anticipation of future support for
    floating-point numbers within a similar framework, for which the
    abbreviation 'FPnum' would have been ambiguous."""

    count_init = 0
    count_frac = 0
    def __init__(self, val=0L, family=None):
        if family is None: family = _defaultFamily
        FXnum.__init__(self, val, family)
        FPnum.count_init += 1
        if FPnum.count_init == 1:
            import sys
            print >> sys.stderr, \
                '/**** spfpm-0.3 (FixedPoint) **************\\\n' \
                '| PLEASE NOTE:                             |\n' \
                '| The classname "FPnum" is now deprecated. |\n' \
                '| Please use "FXnum" instead. Thanks.      |\n' \
                '\\******************************************/'

    def SetFraction(n_bits=32):
        global _defaultFamily
        _defaultFamily = FXfamily(n_bits)
        FPnum.count_frac += 1
        if FPnum.count_frac == 1:
            import sys
            print >> sys.stderr, \
                '/**** spfpm-0.3 (FixedPoint) **************************\\\n' \
                '| PLEASE NOTE:                                         |\n' \
                '| The "FPnum.SetFraction()" method has been superseded |\n' \
                '| by the FXfamily class, which allows                  |\n' \
                '| multiple resolutions to coexist.                     |\n' \
                '| Please use "FXfamily" instead. Thanks.               |\n' \
                '\\******************************************************/'
    SetFraction = staticmethod(SetFraction)


if __name__ == "__main__":
    pass
