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
"""


class FPnum(object):
    fraction_bits = 64
    scale = 1L << fraction_bits
    round = 1L << (fraction_bits - 1)

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

    def __mul__(self, other):
        """Multiply by another number"""
        if not isinstance(other, FPnum): other = FPnum(other)
        new = FPnum()
        new.scaledval = (self.scaledval * other.scaledval + FPnum.round) / FPnum.scale
        return new

    def __div__(self, other):
        """Divide by another number"""
        if not isinstance(other, FPnum): other = FPnum(other)
        new = FPnum()
        new.scaledval = (self.scaledval * FPnum.scale + FPnum.round) / other.scaledval
        return new

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
    def sqrt(self):
        """Compute square-root of given number"""
        # calculate crude initial approximation:
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
        ex = FPnum(1)
        term = FPnum(1)
        idx = FPnum(1)
        while True:
            term *= self / idx
            ex += term
            idx += FPnum(1)
            if term.scaledval == 0: break
        return ex

    def sincos(self):
        """Compute sine & cosine of given number (as angle in radians)"""
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
