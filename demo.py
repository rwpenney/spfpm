#!/usr/bin/python3
# Demonstration of Simple Python Fixed-Point Module
# (C)Copyright 2006-2020, RW Penney

from __future__ import print_function
import argparse, time
from collections import OrderedDict
try:
    import matplotlib, numpy
    import matplotlib.pyplot as plt
    HAVE_MATPLOTLIB = True
except ImportError:
    HAVE_MATPLOTLIB = False

from FixedPoint import FXfamily, FXnum, FXoverflowError


def basicDemo():
    """Basic demonstration of roots & exponents at various accuracies"""

    for resolution in [8, 32, 80, 274]:
        family = FXfamily(resolution)
        val = 2

        print('=== {0} bits ==='.format(resolution))
        rt = family(val).sqrt()
        print('sqrt(' + str(val) + ')~ ' + str(rt))
        print('sqrt(' + str(val) + ')^2 ~ ' + str(rt * rt))
        print('exp(1) ~ ' + str(family.exp1))
        print()


def overflowDemo():
    """Illustrate how finite range limits calculation of exponents"""

    res = 20
    print('=== {0}-bit fractional part ==='.format(res))
    for intsize in [4, 8, 16, 32]:
        family = FXfamily(res, intsize)
        x = family(0.0)
        step = 0.1
        while True:
            try:
                ex = x.exp()
            except FXoverflowError:
                print('{0:2d}-bit integer part: exp(x) overflows near x={1:.3g}'.format(intsize, float(x)))
                break
            x += step
    print()


def speedDemo():
    """calculate indicative speed of floating-point operations"""

    print('=== speed test ===')
    for res, count in [ (16, 10000), (32, 10000),
                        (64, 10000), (128, 10000),
                        (256, 10000), (512, 10000) ]:
        fam = FXfamily(res)
        x = fam(0.5)
        lmb = fam(3.6)
        one = fam(1.0)
        t0 = time.perf_counter()
        for i in range(count):
            # use logistic-map in chaotic region:
            x = lmb * x * (one - x)
        t1 = time.perf_counter()
        ops = count * 3
        Dt = t1 - t0
        print('{0} {1}-bit arithmetic operations in {2:.2f}s ~ {3:.2g} FLOPS' \
                .format(ops, res, Dt, (ops / Dt)))

    for res, count in [ (4, 10000), (8, 10000), (12, 10000),
                        (24, 10000), (48, 10000), (128, 10000),
                        (512, 10000) ]:
        fam = FXfamily(res, 4)
        x = fam(2)
        t0 = time.perf_counter()
        for i in range(count):
            y = x.sqrt()
        t1 = time.perf_counter()
        Dt = (t1 - t0)
        print('{} {}-bit square-roots in {:.3g}s ~ {:.3g}/ms' \
                .format(count, res, Dt, count*1e-3/Dt))


def printBaseDemo():
    res = 60
    pi = FXfamily(res).pi

    print('==== Pi at {}-bit resolution ===='.format(res))
    print('decimal: {}'.format(pi.toDecimalString()))
    print('binary: {}'.format(pi.toBinaryString()))
    print('octal: {}'.format(pi.toBinaryString(3)))
    print('hex: {}'.format(pi.toBinaryString(4)))


def piPlot():
    """Plot graph of approximations to Pi"""

    b_min, b_max = 8, 25
    pi_true = FXfamily(b_max + 40).pi
    pipoints = []
    for res in range(b_min, b_max+1):
        val = 4 * FXnum(1, FXfamily(res)).atan()
        pipoints.append([res, val])
    pipoints = numpy.array(pipoints)
    truepoints = numpy.array([[b_min, pi_true], [b_max, pi_true]])

    plt.xlabel('bits')
    plt.ylabel(r'$4 \tan^{-1} 1$')
    plt.xlim([b_min, b_max])
    plt.ylim([3.13, 3.16])
    plt.grid(True)
    for arr, style in ((truepoints, '--'), (pipoints, '-')):
        plt.plot(arr[:,0], arr[:,1], ls=style)
    plt.show()


class ConstAccuracyPlot(object):
    """Plot graph of fractional bits wasted due to accumulated roundoff."""

    @classmethod
    def calcConsts(cls, fam, famOnly=False):
        """Use various methods to compute constant to given precision."""
        return ( fam.unity, FXnum(1, fam) )

    @classmethod
    def getLabels(cls):
        """Sequence of labels to use when plotting accuracy graph"""
        return ( r'1_{family}', '1' )

    @staticmethod
    def lostbits(x, x_acc):
        """Estimate of least-significant bits lost in approximation"""
        fam_acc = x_acc.family
        eps = (FXnum(x, fam_acc) - x_acc)
        return float(abs(eps).log() / fam_acc.log2
                        + x.family.resolution)

    @classmethod
    def draw(cls):
        losses = []
        for bits in range(4, 500, 4):
            fam_acc = FXfamily(bits + 40)
            fam = FXfamily(bits)
            const_true = cls.calcConsts(fam_acc, famOnly=True)[0]

            losses.append([ bits ] +
                          [ cls.lostbits(apx, const_true)
                                for apx in cls.calcConsts(fam) ])
        losses = numpy.array(losses)

        plt.xlabel('resolution bits')
        plt.ylabel('error bits')
        plt.grid(True)
        for colno, label in enumerate(cls.getLabels(), 1):
            plt.plot(losses[:,0], losses[:,colno], label=label)
        plt.legend(loc='best', fontsize='small')
        plt.show()


class PiAccuracyPlot(ConstAccuracyPlot):
    @classmethod
    def calcConsts(cls, fam, famOnly=False):
        consts = [ fam.pi ]
        if not famOnly:
            consts.append(6 * FXnum(0.5, fam).asin())
            consts.append(4 *  ( 4 * (1 / FXnum(5, fam)).atan()
                                - (1 / FXnum(239, fam)).atan() ))
        return consts

    @classmethod
    def getLabels(cls):
        return ( r'$\pi_{family}$',
                 r'$6 \sin^{-1} \frac{1}{2}$',
                 r'$\pi_{Machin}$' )


class Exp1AccuracyPlot(ConstAccuracyPlot):
    @classmethod
    def calcConsts(cls, fam, famOnly=False):
        consts = [ fam.exp1 ]
        if not famOnly:
            consts.append(1.0 / (FXnum(-0.5, fam).exp() ** 2))
        return consts

    @classmethod
    def getLabels(cls):
        return ( r'$e_{family}$',
                 r'$(e^{-1/2})^{-2}$' )


class Log2AccuracyPlot(ConstAccuracyPlot):
    @classmethod
    def calcConsts(cls, fam, famOnly=False):
        consts = [ fam.log2 ]
        if not famOnly:
            consts.append((2 * FXnum(3, fam).log()
                            - (FXnum(9, fam) / 8).log()) / 3)
        return consts

    @classmethod
    def getLabels(cls):
        return ( r'$\log2_{family}$',
                 r'$(\log9 - \log(9/8))/3$' )


def main():
    demos = OrderedDict([
        ('basic',       basicDemo),
        ('overflow',    overflowDemo),
        ('speed',       speedDemo),
        ('printing',    printBaseDemo) ])
    if HAVE_MATPLOTLIB:
        demos['piplot'] = piPlot
        demos['piaccplot'] = PiAccuracyPlot.draw
        demos['expaccplot'] = Exp1AccuracyPlot.draw
        demos['log2accplot'] = Log2AccuracyPlot.draw

    parser = argparse.ArgumentParser(
                description='Rudimentary demonstrations of'
                            ' the Simple Python Fixed-point Module (SPFPM)')
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('demos', nargs='*',
            help='Demo applications ({})'.format('/'.join(demos.keys())))
    args = parser.parse_args()

    if args.all or not args.demos:
        args.demos = list(demos.keys())

    for demoname in args.demos:
        demos[demoname]()


if __name__ == "__main__":
    main()

# vim: set ts=4 sw=4 et:
