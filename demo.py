#!/usr/bin/python
# demonstration of Simple Python Fixed-Point Module
# $Revision$, $Date$
# Copyright 2006-2007, RW Penney


import FixedPoint


if __name__ == "__main__":
    # basic demonstration of roots & exponents at various accuracies:
    resolution = 6
    while resolution <= 384:
        print '=== ' + str(resolution) + 'bits ==='
        FixedPoint.FPnum.SetFraction(resolution)
        val = 2
        rt = FixedPoint.FPnum(val).sqrt()
        print 'sqrt(' + str(val) + ')~ ' + str(rt)
        print 'sqrt(' +str(val) + ')^2 ~ ' + str(rt * rt)
        print 'exp(1) = ', FixedPoint.FPnum(1).exp()
        print

        resolution *= 4
