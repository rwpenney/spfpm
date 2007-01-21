#!/usr/bin/python
# demonstration of Simple Python Fixed-Point Module
# $Revision$, $Date$
# Copyright 2006-2007, RW Penney


import FixedPoint


if __name__ == "__main__":
    # basic demonstration of roots & exponents at various accuracies:
    for resolution in [8, 32, 80, 274]:
        family = FixedPoint.FXfamily(resolution)
        val = 2

        print '=== ' + str(resolution) + 'bits ==='
        rt = FixedPoint.FXnum(val, family).sqrt()
        print 'sqrt(' + str(val) + ')~ ' + str(rt)
        print 'sqrt(' +str(val) + ')^2 ~ ' + str(rt * rt)
        print 'exp(1) = ', FixedPoint.FXnum(1, family).exp()
        print
