#!/usr/bin/python
# Estimate accuracy of Pi calculated with varying fixed-point resolutions
# $Revision$, $Date$
# RW Penney, January 2009

import FixedPoint

def quant(family):
    return 4 * FixedPoint.FXnum(1, family).atan()
    #return FixedPoint.FXnum(1, family).exp()
    #return FixedPoint.FXnum(7, family).log()

def main():
    maxres = 200

    accres = maxres + (maxres / 4) + 20
    accfam = FixedPoint.FXfamily(accres)
    accval = quant(accfam)

    for res in range(4, maxres):
        fam = FixedPoint.FXfamily(res)
        val = quant(fam)
        delta = abs(FixedPoint.FXnum(val, accfam) - accval)
        err = float(-delta.log() / accfam.GetLog2())
        print res, err

if __name__ == "__main__":
    main()

# vim: set ts=4 sw=4 et:
