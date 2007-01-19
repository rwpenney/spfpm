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
    x = FPnum(2)

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

class FPfamily(object):
    def __init__(self, n_bits=64):
        self.fraction_bits = n_bits         # bits to right of binary point
        self.scale = 1L << n_bits
        self.round = 1L << (n_bits - 1)
        self.exp1 = None                    # cache of exp(1)
        self.log2 = None                    # cache of log(2)

    def __repr__(self):
        return 'FPfamily(%d)' % (self.fraction_bits)

    def __eq__(self, other):
        if isinstance(other, FPfamily):
            return self.fraction_bits == other.fraction_bits
        else:
            return false

    def __ne__(self, other):
        if isinstance(other, FPfamily):
            return self.fraction_bits != other.fraction_bits
        else:
            return true

    def GetExp1(self):
        """return cached value of exp(1)"""
        if self.exp1 is None:
            self.exp1 = FPnum(1, self)._rawexp()
        return self.exp1

    def GetLog2(self):
        """return cached value of log(2)"""
        if self.log2 is None:
            self.log2 = FPnum(2, self)._rawlog()
        return self.log2

    def Convert(self, other, other_val):
        """convert number from different number of fraction-bits"""
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

_defaultFamily = FPfamily()



class FPexception(TypeError):
    """Signal that family-types of FPnums in binary operation are mismatched"""



class FPnum(object):
    def __init__(self, val=0L, family=_defaultFamily):
        assert isinstance(family, FPfamily)
        self.family = family
        if isinstance(val, FPnum):
            self.scaledval = family.Convert(val.family, val.scaledval)
        elif isinstance(val, list):
            sval = val[0]
            self.scaledval = sval
        else:
            self.scaledval = long(val * family.scale)

    def __repr__(self):
        return 'FPnum([%d], %s)' % (self.scaledval, self.family.__repr__())

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
        """turn number into FPnum or check that it is in same family"""
        if isinstance(other, FPnum):
            # binary operations must involve members of same family
            if not self.family is other.family:
                raise FPexception, 1
        else:
            # automatic casting from types other than FPnum is allowed:
            other = FPnum(other, self.family)
        return other

    # unary arithmetic operations:
    def __neg__(self):
        """Change sign"""
        new = FPnum()
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
        new = FPnum(family=self.family)
        new.scaledval = self.scaledval + other.scaledval
        return new

    def __radd__(self, other):
        return FPnum(other, self.family) + self

    def __sub__(self, other):
        """Subtract another number"""
        other = self._CastOrFail_(other)
        new = FPnum(family=self.family)
        new.scaledval = self.scaledval - other.scaledval
        return new

    def __rsub__(self, other):
        return FPnum(other, self.family) - self

    def __mul__(self, other):
        """Multiply by another number"""
        other = self._CastOrFail_(other)
        new = FPnum(family=self.family)
        new.scaledval = (self.scaledval * other.scaledval + self.family.round) / self.family.scale
        return new

    def __rmul__(self, other):
        return FPnum(other, self.family) * self

    def __div__(self, other):
        """Divide by another number"""
        other = self._CastOrFail_(other)
        new = FPnum(family=self.family)
        new.scaledval = (self.scaledval * self.family.scale + self.family.round) / other.scaledval
        return new

    def __rdiv__(self, other):
        return FPnum(other, self.family) / self

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
            return FPnum(1, self.family)
        if isinstance(other, int) or isinstance(other, long):
            ipwr = other
            frac = FPnum(1, self.family)
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
        result = FPnum(1, self.family)
        term = self
        while pwr != 0:
            if pwr & 1:
                result *= term
            pwr >>= 1
            term *= term
        if invert:
            result = FPnum(1, self.family) / result
        return result

    def sqrt(self):
        """Compute square-root of given number"""
        # calculate crude initial approximation:
        assert self.scaledval >= 0
        rt = FPnum(family=self.family)
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
        ex = FPnum(1, self.family)
        term = FPnum(1, self.family)
        idx = FPnum(1, self.family)
        while True:
            term *= self / idx
            ex += term
            idx += FPnum(1, self.family)
            if term.scaledval == 0: break
        return ex

    def log(self):
        """Compute (natural) logarithm of given number"""
        thresh = FPnum(2, self.family)
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
        lg = FPnum(0, self.family)
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
        # use double-angle formulae to avoid series with large argument:
        if self.scaledval > 2*self.family.scale or self.scaledval < -2*self.family.scale:
            (sn, cs) = (self / 2).sincos()
            return ((2 * sn * cs), ((cs - sn) * (cs + sn)))

        sn = FPnum(0, self.family)
        cs = FPnum(1, self.family)
        term = FPnum(1, self.family)
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



if __name__ == "__main__":
    pass
