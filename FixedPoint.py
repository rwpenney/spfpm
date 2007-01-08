#!/usr/bin/python
# Simple fixed-point numerical class
# $Revision$, $Date$
# Copyright 2006, RW Penney


# This file is Copyright 2006, RW Penney
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


class FPnum(object):
    fraction_bits = 64                      # bits to right of binary point
    scale = 1L << fraction_bits
    round = 1L << (fraction_bits - 1)
    exp1 = None                             # cache of exp(1)
    log2 = None                             # cache of log(2)

    def __init__(self, val=0L):
        if isinstance(val, FPnum):
            self.scaledval = val.scaledval
        else:
            self.scaledval = long(val * FPnum.scale)

    def SetFraction(n_bits=32):
        # change number of fractional bits (call before creating numbers!)
        FPnum.fraction_bits = n_bits
        FPnum.scale = 1L << n_bits
        FPnum.round = 1L << (n_bits - 1)
        FPnum.exp1 = None
        FPnum.log2 = None
    SetFraction = staticmethod(SetFraction)

    # converstion operations:
    def __int__(self):
        """Cast to (plain) integer"""
        return int((self.scaledval + FPnum.round) / FPnum.scale)

    def __long__(self):
        """Cast to long integer"""
        return long((self.scaledval + FPnum.round) / FPnum.scale)

    def __float__(self):
        """Cast to floating-point"""
        return float(self.scaledval) / float(FPnum.scale)

    # unary arithmetic operations:
    def __neg__(self):
        """Change sign"""
        new = FPnum()
        new.scaledval = -self.scaledval
        return new

    # arithmetic comparison tests:
    def __eq__(self, other):
        """Equality test"""
        if not isinstance(other, FPnum): other = FPnum(other)
        return self.scaledval == other.scaledval

    def __ne__(self, other):
        """Inequality test"""
        if not isinstance(other, FPnum): other = FPnum(other)
        return self.scaledval != other.scaledval

    def __ge__(self, other):
        """Greater-or-equal test"""
        if not isinstance(other, FPnum): other = FPnum(other)
        return self.scaledval >= other.scaledval

    def __gt__(self, other):
        """Greater-than test"""
        if not isinstance(other, FPnum): other = FPnum(other)
        return self.scaledval > other.scaledval

    def __le__(self, other):
        """Less-or-equal test"""
        if not isinstance(other, FPnum): other = FPnum(other)
        return self.scaledval <= other.scaledval

    def __lt__(self, other):
        """Greater-than test"""
        if not isinstance(other, FPnum): other = FPnum(other)
        return self.scaledval < other.scaledval

    def __nonzero__(self):
        """Test for non-zero"""
        if not isinstance(other, FPnum): other = FPnum(other)
        return (self.scaledval != 0)

    # arithmetic combinations:
    def __add__(self, other):
        """Add another number"""
        if not isinstance(other, FPnum): other = FPnum(other)
        new = FPnum()
        new.scaledval = self.scaledval + other.scaledval
        return new

    def __iadd__(self, other):
        """In-place addition"""
        if not isinstance(other, FPnum): other = FPnum(other)
        self.scaledval += other.scaledval
        return self

    def __radd__(self, other):
        return FPnum(other) + self

    def __sub__(self, other):
        """Subtract another number"""
        if not isinstance(other, FPnum): other = FPnum(other)
        new = FPnum()
        new.scaledval = self.scaledval - other.scaledval
        return new

    def __isub__(self, other):
        """In-place subtraction"""
        if not isinstance(other, FPnum): other = FPnum(other)
        self.scaledval -= other.scaledval
        return self

    def __rsub__(self, other):
        return FPnum(other) - self

    def __mul__(self, other):
        """Multiply by another number"""
        if not isinstance(other, FPnum): other = FPnum(other)
        new = FPnum()
        new.scaledval = (self.scaledval * other.scaledval + FPnum.round) / FPnum.scale
        return new

    def __rmul__(self, other):
        return FPnum(other) * self

    def __div__(self, other):
        """Divide by another number"""
        if not isinstance(other, FPnum): other = FPnum(other)
        new = FPnum()
        new.scaledval = (self.scaledval * FPnum.scale + FPnum.round) / other.scaledval
        return new

    def __rdiv__(self, other):
        return FPnum(other) / self

    # printing/converstion routines:
    def __str__(self):
        """Convert number (as decimal) into string"""
        val = self.scaledval
        rep = ''
        if self.scaledval < 0:
            rep = '-'
            val *= -1
        whole = val / FPnum.scale
        frac = val - FPnum.scale * whole
        rep += str(whole)
        if frac != 0:
            rep += '.'
            idx = 0
            while idx < (FPnum.fraction_bits / 3) and frac != 0:
                frac *= 10L
                q = frac / FPnum.scale
                rep += str(q)
                frac -= q * FPnum.scale
                idx += 1
        return rep

    # mathematical functions:
    def __pow__(self, other, modulus=None):
        assert modulus is None
        assert isinstance(other, int) or isinstance(other, long)
        if other >= 0:
            pwr = other
            invert = False
        else:
            pwr = -other
            invert = True
        # compute (integer) power by repeated squaring:
        result = FPnum(1)
        term = self
        while pwr != 0:
            if pwr & 1:
                result *= term
            pwr >>= 1
            term *= term
        if invert:
            result = FPnum(1) / result
        return result

    def sqrt(self):
        """Compute square-root of given number"""
        # calculate crude initial approximation:
        assert self.scaledval >= 0
        rt = FPnum()
        rt.scaledval = 1L << (FPnum.fraction_bits / 2)
        val = self.scaledval
        while val > 0:
            val >>= 2
            rt.scaledval <<= 1
        # refine approximation by Newton iteration:
        while True:
            delta = (rt - self / rt) / FPnum(2)
            rt -= delta
            if delta.scaledval == 0: break
        return rt

    def exp(self):
        """Compute exponential of given number"""
        if FPnum.exp1 is None:
            FPnum.exp1 = FPnum(1)._rawexp()
        pwr = long(self)
        return (self - pwr)._rawexp() * (FPnum.exp1 ** pwr)

    def _rawexp(self):
        ex = FPnum(1)
        term = FPnum(1)
        idx = FPnum(1)
        while True:
            term *= self / idx
            ex += term
            idx += FPnum(1)
            if term.scaledval == 0: break
        return ex

    def log(self):
        """Compute (natural) logarithm of given number"""
        assert self.scaledval > 0
        if FPnum.log2 is None:
            FPnum.log2 = FPnum(2)._rawlog()
        count = 0
        val = FPnum(self)
        while val > 2.0:
            val /= 2
            count += 1
        while val < 0.5:
            val *= 2
            count -= 1
        return val._rawlog() + count * FPnum.log2

    def _rawlog(self):
        lg = FPnum(0)
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
        if self.scaledval > 2*FPnum.scale or self.scaledval < -2*FPnum.scale:
            (sn, cs) = (FPnum(self) / 2).sincos()
            return ((2 * sn * cs), ((cs - sn) * (cs + sn)))

        sn = FPnum(0)
        cs = FPnum(1)
        term = FPnum(1)
        idx = 1
        while (True):
            term *= self / FPnum(idx)
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
    # basic demonstration of roots & exponents at various accuracies:
    resolution = 6
    while resolution <= 384:
        print '=== ' + str(resolution) + 'bits ==='
        FPnum.SetFraction(resolution)
        val = 2
        rt = FPnum(val).sqrt()
        print 'sqrt(' + str(val) + ')~ ' + str(rt)
        print 'sqrt(' +str(val) + ')^2 ~ ' + str(rt * rt)
        print 'exp(1) = ', FPnum(1).exp()
        print

        resolution *= 4
