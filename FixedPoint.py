#!/usr/bin/python3
# Simple Python Fixed-Point Module (SPFPM)
# (C)Copyright 2006-2014, RW Penney


# This file is (C)Copyright 2006-2014, RW Penney
# and is released under the Python-2.4.2 license
# (see http://www.python.org/psf/license),
# it therefore comes with NO WARRANTY, and NO CLAIMS OF FITNESS FOR ANY PURPOSE.
# However, the author welcomes *constructive* feedback
# and bug-fixes via: rwpenney 'AT' users 'DOT' sourceforge 'DOT' net


"""
The Simple Python Fixed-Point Module (SPFPM) provides objects of types
FXnum and FXfamily which implement basic mathematical operations
on fixed-point binary numbers (i.e. having a fixed number of
fractional binary digits, with the number of integer digits being either
arbitrary or subject to a user-defined limit).

FXnum objects exist within a user-controllable collection of families
managed by the FXfamily class, which sets the number of fractional
& integer digits for each family. This can be used, for example,
to ensure that a set of 8-bit quantities can be manipulated consistently
and kept separate from a set of 200-bit quantities in the same program.
Conversion between FXnum objects in different families is supported,
but solely through an explicit cast.

>>> x = FXnum(2.1)                  # default FXfamily, with 64-bits
>>> print(x)
2.100000000000000088817
>>> x = FXnum(21) / 10              # fractional error ~1/2^64 or ~5e-20
>>> print(x)
2.099999999999999999967
>>> rx = x.sqrt()                   # rx created in same family as x
>>> print(rx)
1.449137674618943857354
>>> v = x + 2 * rx
>>> print(v)
4.998275349237887714675

>>> y = FXnum(3.2, FXfamily(12))    # lower-precision 12-bit number
>>> ly = y.log()                    # ly created in same family as y
>>> print(ly)                       # fractional error ~1/2^12 or ~2e-4
1.1628
>>> print(ly.exp())
3.1987
>>> fy = float(y)
>>> print(fy)
3.199951171875

>>> # a = x + y                     # throws exception - different families
>>> a = x + FXnum(y, _defaultFamily)
>>> print(a)
5.300073242187499999967
>>> b = rx + x                      # ok - same families
>>> # c = rx + ly                   # throws exception - different families
>>> d = ly + y                      # ok - same families

>>> a = FXnum(1.4, FXfamily(12, 4)) # limit magnitude to 2^(4-1)
>>> print(a)
1.3999
>>> print(a * 5, a * -5)
6.9995 -6.9995
>>> #print(a * 6, a * -6)           # throws exception indicating overflow

>>> fam = FXfamily(200)
>>> print(fam.pi)
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


SPFPM_VERSION = '1.1'


class FXfamily(object):
    """Descriptor of the accuracy of a set of fixed-point numbers.

    This class defines the fixed-point resolution of a set of FXnum objects.
    All arithmetic operations between FXnum objects that are
    not explicitly cast into a different FXfamily
    must share the same FXfamily.
    Multiple FXfamily objects can exist within the same application so that,
    for example, sets of 12-bit, 32-bit & 200-bit quantities
    can be manipulated concurrently.
    """

    def __init__(self, n_bits=64, n_intbits=None):
        self.fraction_bits = n_bits         # Bits to right of binary point
        self.integer_bits = n_intbits       # Bits to left of binary point (including sign)
        self.scale = 1 << n_bits
        self._roundup = 1 << (n_bits - 1)

        try:
            thresh = 1 << (n_bits + n_intbits - 1)
            def validate(scaledval):
                if scaledval >= thresh or scaledval < -thresh:
                    raise FXoverflowError
        except:
            def validate(scaledval): return
        self.validate = validate

        # Cached values of various mathematical constants:
        self._exp1, self._log2, self._pi, self._sqrt2 = (None,) * 4

        # Estimate number of extra bits required for accurate values of Pi etc,
        # assuming worst-case of O(n_bits) operations, each with 1-LSB error:
        self._augbits = 4
        nb = n_bits
        while nb > 0:
            self._augbits += 1
            nb >>= 1

    @property
    def resolution(self):
        """The number of fractional binary digits"""
        return self.fraction_bits

    @property
    def exp1(self):
        """Inverse natural logarithm of unity."""
        if self._exp1 is None:
            # Brute-force calculation of exp(1) using augmented accuracy:
            augfamily = FXfamily(self.fraction_bits + self._augbits)
            augexp = FXnum(1, augfamily)._rawexp()
            arg = 1 / FXnum(4, augfamily)
            q0 = arg._rawexp()
            q1 = q0 * q0
            augexp = q1 * q1
            self._exp1 = FXnum(augexp, self)
        return self._exp1

    @property
    def log2(self):
        """Natural logarithm of two."""
        if self._log2 is None:
            # Brute-force calculation of log(2) using augmented accuracy
            #   via log(2) = log(2^19 / 3^12) + 6log(1 + 1/8):
            augfamily = FXfamily(self.fraction_bits + self._augbits)
            auglog2 = FXnum(2, augfamily)._rawlog()
            three12 = (9 * 9 * 9) * (9 * 9 * 9)
            two19 = 1 << 19
            q0 = FXnum(two19 - three12, augfamily) / FXnum(three12, augfamily)
            q1 = 1 / FXnum(8, augfamily)
            auglog2 = q0._rawlog(isDelta=True) + 6 * q1._rawlog(isDelta=True)
            self._log2 = FXnum(auglog2, self)
        return self._log2

    @property
    def pi(self):
        """Ratio of circle's perimeter to its diameter."""
        if self._pi is None:
            # Brute-force calculation of 8*atan(pi/8) using augmented accuracy:
            augfamily = FXfamily(self.fraction_bits + self._augbits)
            tan8 = (augfamily.sqrt2 - 1)
            augpi = 8 * tan8._rawarctan()
            self._pi = FXnum(augpi, self)
        return self._pi

    @property
    def sqrt2(self):
        """Square-root of two."""
        if self._sqrt2 is None:
            augfamily = FXfamily(self.fraction_bits + self._augbits)
            x = FXnum(3, augfamily) >> 1
            while True:
                # Apply Newton-Raphson iteration to f(x)=2/(x*x)-1:
                delta = (x * (2 - x * x)) >> 2
                x += delta
                if abs(delta.scaledval) <= 1:
                    break
            self._sqrt2 = FXnum(x, self)
        return self._sqrt2

    @property
    def unity(self):
        """The multiplicative identity."""
        return FXnum(1, self)

    @property
    def zero(self):
        """The additive identity."""
        return FXnum(0, self)

    def __hash__(self):
        return hash(self.fraction_bits)

    def __repr__(self):
        return 'FXfamily(n_bits={}, n_intbits={})'.format(self.fraction_bits,
                                                          self.integer_bits)

    def __eq__(self, other):
        try:
            return self.fraction_bits == other.fraction_bits
        except AttributeError:
            pass
        return false

    def __ne__(self, other):
        try:
            return self.fraction_bits != other.fraction_bits
        except AttributeError:
            pass
        return true

    def Convert(self, other, other_val):
        """Convert number from different number of fraction-bits"""
        bit_inc = self.fraction_bits - other.fraction_bits
        if bit_inc == 0:
            return other_val
        elif bit_inc > 0:
            new_val = other_val << bit_inc
            if other_val > 0:
                new_val |= 1 << (bit_inc - 1)
            else:
                new_val |= ((1 << (bit_inc -1)) - 1)
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

class FXoverflowError(FXexception):
    """Signal that value has overflowed its most-significant bit"""

class FXfamilyError(FXexception, TypeError):
    """Signal that family-types of FXnums in binary operation are mismatched"""

class FXbrokenError(FXexception):
    """Signal some form of internal error, e.g. broken logic"""



class FXnum(object):
    """Representation of a binary fixed-point real number."""

    def __init__(self, val=0, family=_defaultFamily, **kwargs):
        self.family = family
        converter = family.Convert
        try:
            # assume that val is similar to FXnum:
            self.scaledval = converter(val.family, val.scaledval)
        except AttributeError:
            self.scaledval = kwargs.get('scaled_value',
                                        int(val * family.scale))
        self.family.validate(self.scaledval)

    def __hash__(self):
        return hash(self.scaledval) ^ hash(self.family)

    def __repr__(self):
        """Create unambiguous string representation of self"""
        return 'FXnum(family={}, scaled_value={})'.format(self.family,
                                                          self.scaledval)

    # conversion operations:
    def __int__(self):
        """Cast to integer"""
        if self.scaledval >= 0:
            return int(self.scaledval // self.family.scale)
        else:
            return int((self.scaledval + self.family.scale - 1) // self.family.scale)

    def __float__(self):
        """Cast to floating-point"""
        return float(self.scaledval) / float(self.family.scale)

    def _CastOrFail_(self, other):
        """Turn number into FXnum or check that it is in same family"""
        try:
            # Binary operations must involve members of same family
            if not self.family is other.family:
                raise FXfamilyError(1)
        except AttributeError:
            # Automatic casting from types other than FXnum is allowed:
            other = FXnum(other, self.family)
        return other

    # Unary arithmetic operations:
    def __abs__(self):
        """Modulus"""
        if self.scaledval < 0:
            return -self
        else:
            return self

    def __neg__(self):
        """Change sign"""
        return FXnum(family=self.family,
                     scaled_value=-self.scaledval)

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

    def __bool__(self):
        """Test for truth/falsehood"""
        return (self.scaledval != 0)

    def __nonzero__(self):
        """Test for non-zero"""
        return (self.scaledval != 0)

    # arithmetic combinations:
    def __add__(self, other):
        """Add another number"""
        other = self._CastOrFail_(other)
        return FXnum(family=self.family,
                     scaled_value=(self.scaledval + other.scaledval))

    def __radd__(self, other):
        return FXnum(other, self.family) + self

    def __sub__(self, other):
        """Subtract another number"""
        other = self._CastOrFail_(other)
        return FXnum(family=self.family,
                     scaled_value=(self.scaledval - other.scaledval))

    def __rsub__(self, other):
        return FXnum(other, self.family) - self

    def __mul__(self, other):
        """Multiply by another number"""
        other = self._CastOrFail_(other)
        return FXnum(family=self.family,
                     scaled_value=((self.scaledval * other.scaledval
                                            + self.family._roundup)
                                        // self.family.scale))

    def __rmul__(self, other):
        return FXnum(other, self.family) * self

    def __lshift__(self, shift):
        return FXnum(family=self.family,
                     scaled_value=(self.scaledval << shift))

    def __rshift__(self, shift):
        return FXnum(family=self.family,
                     scaled_value=(self.scaledval >> shift))

    def __truediv__(self, other):
        """Divide by another number (without truncation)"""
        other = self._CastOrFail_(other)
        return FXnum(family=self.family,
                     scaled_value=((self.scaledval * self.family.scale
                                        + self.family._roundup)
                                    // other.scaledval))
    __div__ = __truediv__

    def __rtruediv__(self, other):
        return FXnum(other, self.family) / self
    __rdiv__ = __rtruediv__

    # printing/converstion routines:
    def __str__(self):
        """Convert number (as decimal) into string"""
        # despite rebinding costs, list+join idiom appears slower here
        # than string concatenation building 'rep' from successive digits
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
                frac *= 10
                q = frac // self.family.scale
                rep += str(q)
                frac -= q * self.family.scale
                idx += 1
        return rep

    # mathematical functions:
    def __pow__(self, other, modulus=None):
        """Evaluate self ^ other"""
        assert modulus is None
        if self == 0:
            return self.family.unity
        ipwr = int(other)
        rmdr = (other -ipwr)
        if rmdr == 0:
            frac = self.family.unity
        else:
            frac = (rmdr * self.log()).exp()
        return self.intpower(ipwr) * frac

    def __rpow__(self, other):
        return FXnum(other, self.family) ** self

    def intpower(self, pwr):
        """Compute integer power by repeated squaring"""
        assert isinstance(pwr, int)
        invert = False
        if pwr < 0:
            pwr *= -1
            invert = True
        result = self.family.unity
        term = self
        while True:
            if pwr & 1:
                result *= term
            pwr >>= 1
            if not pwr:
                break
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
        rt = FXnum(family=self.family,
                   scaled_value=(1 << (self.family.fraction_bits // 2)))
        val = self.scaledval
        while val > 0:
            val >>= 2
            rt.scaledval <<= 1
        # refine approximation by Newton iteration:
        while True:
            delta = (rt - self / rt) >> 1
            rt -= delta
            if delta.scaledval == 0: break
        return rt

    def exp(self):
        """Compute exponential of given number"""
        pwr = int(self)
        return (self - pwr)._rawexp() * (self.family.exp1 ** pwr)

    def _rawexp(self):
        """Brute-force exponential of given number (assumed smallish)"""
        ex = self.family.unity
        term = self.family.unity
        idx = 1
        while True:
            term *= self / idx
            ex += term
            idx += 1
            if term.scaledval == 0: break
        return ex

    def log(self):
        """Compute (natural) logarithm of given number"""
        if self.scaledval <= 0:
            raise FXdomainError
        elif self == 1:
            return FXnum(0, self.family)
        uprthresh = FXnum(1.6, self.family)
        lwrthresh = uprthresh / 2
        count = 0
        val = self
        while val > uprthresh:
            val /= 2
            count += 1
        while val < lwrthresh:
            val *= 2
            count -= 1
        return val._rawlog() + count * self.family.log2

    def _rawlog(self, isDelta=False):
        """Compute (natural) logarithm of given number (assumed close to 1)"""
        lg = self.family.zero
        if isDelta:
            z = self / (self + 2)
        else:
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
        arg = self
        reflect = False
        if self < 0:
            arg *= -1
            reflect = True
        if arg <= 0.5:
            cs2 = 1 - arg * arg
            asn = (arg / cs2.sqrt()).atan()
        else:
            # apply 1-cos2t transformation:
            tn2 = (1 - arg) / (1 + arg)
            if tn2 < 0: raise FXdomainError
            asn = self.family.pi / 2 - 2 * (tn2.sqrt()).atan()
        if reflect: asn *= -1
        return asn

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
        if arg <= 0.5:
            sn2 = 1 - arg * arg
            acs = self.family.pi / 2 - (arg / sn2.sqrt()).atan()
        else:
            # apply 1-cos2t transformation:
            tn2 = (1 - arg) / (1 + arg)
            if tn2 < 0: raise FXdomainError
            acs = 2 * (tn2.sqrt()).atan()
        if reflect: acs = self.family.pi - acs
        return acs

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
        """Helper function for reducing angle modulo 2.Pi"""
        reflect = False
        ang = self
        if ang < 0:
            ang *= -1
            reflect = True
        # Find nearest multiple of pi/2:
        halfpi = self.family.pi / 2
        idx = int(ang / halfpi + 0.5)
        ang -= idx * halfpi
        return (ang, idx, reflect)

    def _rawQsine(self, doCos=False, doHyp=False):
        """Helper function for brute-force calculation of sine & cosine"""
        sn = self.family.zero
        if doHyp:
            x2 = self * self
        else:
            x2 = -self * self
        term = self.family.unity
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
            ang = self.family.pi / 2 - ang
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


if __name__ == "__main__":
    import doctest
    try:
        doctest.testmod()
    except TypeError:
        print("*** Problems running doctest module ***")

# vim: set ts=4 sw=4 et:
