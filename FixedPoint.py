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


"""
The Simple Python Fixed-Point Module (SPFPM) provides objects of types
FXnum and FXfamily which implement basic mathematical operations
on fixed-point binary numbers (i.e. having a fixed number of
fractional binary digits, with an arbitrary number of integer digits).

FXnum objects exist within a user-controllable collection of families managed
by the FXfamily class, which sets the number of fractional digits for
each family. This can be used, for example to ensure that a set of
8-bit quantities can be manipulated consistently and kept separate from
a set of 200-bit quantities in the same program. Conversion between
FXnum objects in different families is supported, but solely through
an explicit cast.

>>> x = FXnum(2.1)                  # default FXfamily, with 64-bits
>>> print x
2.100000000000000088817
>>> x = FXnum(21) / 10              # fractional error ~1/2^64 or ~5e-20
>>> print x
2.099999999999999999967
>>> rx = x.sqrt()                   # rx created in same family as x
>>> print rx
1.449137674618943857354
>>> v = x + 2 * rx
>>> print v
4.998275349237887714675

>>> y = FXnum(3.2, FXfamily(12))    # lower-precision 12-bit number
>>> ly = y.log()                    # ly created in same family as y
>>> print ly                        # fractional error ~1/2^12 or ~2e-4
1.1628
>>> print ly.exp()
3.1987
>>> fy = float(y)
>>> print fy
3.19995117188

>>> # a = x + y                     # throws exception - different families
>>> a = x + FXnum(y, _defaultFamily)
>>> print a
5.300073242187499999967
>>> b = rx + x                      # ok - same families
>>> # c = rx + ly                   # throws exception - different families
>>> d = ly + y                      # ok - same families

>>> fam = FXfamily(200)
>>> print fam.GetPi()
3.141592653589793238462643383279502884197169399375105820974944478108

Note:
    Be careful not to assume that a large number of fractional bits within
    a number will necessarily mean large accuracy. For example, computations
    involving exponentiation and logarithms are intrinsically vulnerable to
    magnifying mere rounding errors in their inputs into significant errors
    in their outputs. This is a fact of life with any approximation to
    real arithmetic using finite-precision quantities.

SPFPM is provided as-is, with no warranty of any form.
"""

class FXfamily(object):
    """This class defines the fixed-point resolution of a set of FXnum objects.
    All arithmetic operations between FXnum objects that are
    not explicitly cast into a different FXfamily
    must share the same FXfamily.
    Multiple FXfamily objects can exist within the same application so that,
    for example, sets of 12-bit, 32-bit & 200-bit quantities
    can be manipulated concurrently."""

    def __init__(self, n_bits=64):
        self.fraction_bits = n_bits         # bits to right of binary point
        self.scale = 1L << n_bits
        self.round = 1L << (n_bits - 1)
        self.exp1 = None                    # cache of exp(1)
        self.log2 = None                    # cache of log(2)
        self.Pi = None                      # cache of 3.14159...

    def __hash__(self):
        return hash(self.fraction_bits)

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
        """Find the number of fractional binary digits"""
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


####
# Exceptions
#

class FXexception(ArithmeticError):
    """Base-class of exceptions generated by SPFPM operations"""

class FXdomainError(FXexception):
    """Signal that input argument of mathematical function is unsuitable"""

class FXfamilyError(FXexception, TypeError):
    """Signal that family-types of FXnums in binary operation are mismatched"""

class FXbrokenError(FXexception):
    """Signal some form of internal error, e.g. broken logic"""



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

    def __hash__(self):
        return hash(self.scaledval) ^ hash(self.family)

    def __repr__(self):
        return 'FXnum([%d], %s)' % (self.scaledval, self.family.__repr__())

    # conversion operations:
    def __int__(self):
        """Cast to (plain) integer"""
        if self.scaledval >= 0:
            return int(self.scaledval // self.family.scale)
        else:
            return int((self.scaledval + self.family.scale - 1) // self.family.scale)

    def __long__(self):
        """Cast to long integer"""
        if self.scaledval >= 0:
            return long(self.scaledval // self.family.scale)
        else:
            return long((self.scaledval + self.family.scale - 1) // self.family.scale)

    def __float__(self):
        """Cast to floating-point"""
        return float(self.scaledval) / float(self.family.scale)

    def _CastOrFail_(self, other):
        """turn number into FXnum or check that it is in same family"""
        if isinstance(other, FXnum):
            # binary operations must involve members of same family
            if not self.family is other.family:
                raise FXfamilyError, 1
        else:
            # automatic casting from types other than FXnum is allowed:
            other = FXnum(other, self.family)
        return other

    # unary arithmetic operations:
    def __abs__(self):
        """Modulus"""
        if self.scaledval < 0:
            return -self
        else:
            return self

    def __neg__(self):
        """Change sign"""
        new = FXnum(family=self.family)
        new.scaledval = -self.scaledval
        return new

    def __pos__(self):
        """Identity operation"""
        return self

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
        new.scaledval = (self.scaledval * other.scaledval + self.family.round) // self.family.scale
        return new

    def __rmul__(self, other):
        return FXnum(other, self.family) * self

    def __truediv__(self, other):
        """Divide by another number (without truncation)"""
        other = self._CastOrFail_(other)
        new = FXnum(family=self.family)
        new.scaledval = (self.scaledval * self.family.scale + self.family.round) // other.scaledval
        return new
    __div__ = __truediv__

    def __rtruediv__(self, other):
        return FXnum(other, self.family) / self
    __rdiv__ = __rtruediv__

    # printing/converstion routines:
    def __str__(self):
        """Convert number (as decimal) into string"""
        val = self.scaledval
        rep = ''
        if self.scaledval < 0:
            rep = '-'
            val *= -1
        whole = val // self.family.scale
        frac = val - self.family.scale * whole
        rep += str(whole)
        if frac != 0:
            rep += '.'
            idx = 0
            while idx < (self.family.fraction_bits // 3) and frac != 0:
                frac *= 10L
                q = frac // self.family.scale
                rep += str(q)
                frac -= q * self.family.scale
                idx += 1
        return rep

    # mathematical functions:
    def __pow__(self, other, modulus=None):
        """evaluate self ^ other"""
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

    def __rpow__(self, other):
        return FXnum(other, self.family) ** self

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
        if self.scaledval < 0:
            raise FXdomainError
        elif self.scaledval == 0:
            return self
        # calculate crude initial approximation:
        rt = FXnum(family=self.family)
        rt.scaledval = 1L << (self.family.fraction_bits // 2)
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
        if self.scaledval <= 0:
            raise FXdomainError
        elif self == 1:
            return FXnum(0, self.family)
        thresh = FXnum(2, self.family)
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

    def sin(self):
        """Compute sine of given number (as angle in radians)"""
        (ang, idx, reflect) = self._angnorm()
        idx = idx % 4
        if idx == 0: sn = ang._rawQsine(False)
        elif idx == 1: sn = ang._rawQsine(True)
        elif idx == 2: sn = -ang._rawQsine(False)
        elif idx == 3: sn = -ang._rawQsine(True)
        else: raise FXbrokenError
        if reflect: sn *= -1
        return sn

    def asin(self):
        """Compute inverse sine of given number"""
        if self == 1:
            return self.family.GetPi() / 2
        elif self == -1:
            return -self.family.GetPi() / 2
        else:
            cs2 = 1 - self * self
            if cs2 < 0: raise FXdomainError
            return (self / cs2.sqrt()).atan()

    def cos(self):
        """Compute cosine of given number (as angle in radians)"""
        (ang, idx, reflect) = self._angnorm()
        idx = idx % 4
        if idx == 0: cs = ang._rawQsine(True)
        elif idx == 1: cs = -ang._rawQsine(False)
        elif idx == 2: cs = -ang._rawQsine(True)
        elif idx == 3: cs = ang._rawQsine(False)
        else: raise FXbrokenError
        return cs

    def acos(self):
        """Compute inverse cosine of given number"""
        arg = self
        reflect = False
        if self < 0:
            arg *= -1
            reflect = True
        if arg == 1:
            cs = FXnum(0, self.family)
        elif arg == 0:
            cs = self.family.GetPi() / 2
        else:
            sn2 = 1 - arg * arg
            if sn2 < 0: raise FXdomainError
            cs = (sn2.sqrt() / arg).atan()
        if reflect:
            return self.family.GetPi() - cs
        else:
            return cs

    def sincos(self):
        """Compute sine & cosine of given number (as angle in radians)"""
        (ang, idx, reflect) = self._angnorm()
        osn = ang._rawQsine(False)
        ocs = ang._rawQsine(True)
        # transform according to sin(ang+offset), cos(ang+offset):
        idx = idx % 4
        if idx == 0: (sn, cs) = (osn, ocs)
        elif idx == 1: (sn, cs) = (ocs, -osn)
        elif idx == 2: (sn, cs) = (-osn, -ocs)
        elif idx == 3: (sn, cs) = (-ocs, osn)
        else: raise FXbrokenError
        if reflect: sn *= -1
        return (sn, cs)

    def _angnorm(self):
        """helper function for reducing angle modulo 2.Pi"""
        reflect = False
        ang = self
        if ang < 0:
            ang *= -1
            reflect = True
        # find nearest multiple of pi/2:
        halfpi = self.family.GetPi() / 2
        idx = long(ang / halfpi + 0.5)
        ang -= idx * halfpi
        return (ang, idx, reflect)

    def _rawQsine(self, doCos=False, doHyp=False):
        """helper function for brute-force calculation of sine & cosine"""
        sn = FXnum(0, self.family)
        if doHyp:
            x2 = self * self
        else:
            x2 = -self * self
        term = FXnum(1, self.family)
        if doCos: idx = 1
        else: idx = 2
        while True:
            sn += term
            term *= x2 / (idx * (idx + 1))
            idx += 2
            if term.scaledval == 0: break
        if doCos: return sn
        else: return self * sn

    def tan(self):
        """Compute tangent of given number (as angle in radians)"""
        (sn, cs) = self.sincos()
        return sn / cs

    def atan(self):
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
                '/**** spfpm-0.4 (FixedPoint) **************************\\\n' \
                '| PLEASE NOTE:                                         |\n' \
                '| The classname "FPnum" is now deprecated.             |\n' \
                '| Please use "FXnum" instead. Thanks.                  |\n' \
                '| THIS COMPATIBILTY-LAYER WILL BE REMOVED in SPFPM-0.5 |\n' \
                '\\******************************************************/'

    def SetFraction(n_bits=32):
        global _defaultFamily
        _defaultFamily = FXfamily(n_bits)
        FPnum.count_frac += 1
        if FPnum.count_frac == 1:
            import sys
            print >> sys.stderr, \
                '/**** spfpm-0.4 (FixedPoint) **************************\\\n' \
                '| PLEASE NOTE:                                         |\n' \
                '| The "FPnum.SetFraction()" method has been superseded |\n' \
                '| by the FXfamily class, which allows                  |\n' \
                '| multiple resolutions to coexist.                     |\n' \
                '| Please use "FXfamily" instead. Thanks.               |\n' \
                '\\******************************************************/'
    SetFraction = staticmethod(SetFraction)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
