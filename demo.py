#!/usr/bin/python
# Demonstration of Simple Python Fixed-Point Module
# (C)Copyright 2006-2009, RW Penney


import FixedPoint, time

def basicDemo():
    """Basic demonstration of roots & exponents at various accuracies"""

    for resolution in [8, 32, 80, 274]:
        family = FixedPoint.FXfamily(resolution)
        val = 2

        print('=== {0} bits ==='.format(resolution))
        rt = FixedPoint.FXnum(val, family).sqrt()
        print('sqrt(' + str(val) + ')~ ' + str(rt))
        print('sqrt(' + str(val) + ')^2 ~ ' + str(rt * rt))
        print('exp(1) ~ ' + str(FixedPoint.FXnum(1, family).exp()))
        print()

def overflowDemo():
    """Illustrate how finite range limits calculation of exponents"""

    res = 20
    print('=== {0}-bit fractional part ==='.format(res))
    for intsize in [4, 8, 16, 32, 64]:
        family = FixedPoint.FXfamily(20, intsize)
        x = FixedPoint.FXnum(0.0, family)
        step = 0.1
        while True:
            try:
                ex = x.exp()
            except FixedPoint.FXoverflowError:
                print('{0:2d}-bit integer part: exp(x) overflows at x={1:.3g}'.format(intsize, float(x)))
                break
            x += step
    print()

def speedDemo():
    """calculate indicative speed of floating-point operations"""

    print('=== speed test ===')
    for res, count in [ (16, 10000), (32, 10000), (64, 10000), (128, 10000), (256, 10000), (512, 10000) ]:
        fam = FixedPoint.FXfamily(res)
        x = FixedPoint.FXnum(0.5, fam)
        lmb = FixedPoint.FXnum(3.6, fam)
        one = FixedPoint.FXnum(1.0, fam)
        t0 = time.clock()
        for i in range(0, count):
            # use logistic-map in chaotic region:
            x = lmb * x * (one - x)
        t1 = time.clock()
        ops = count * 3
        Dt = t1 - t0
        print('{0} {1}-bit operations in {2:.2f}s ~ {3:.2g} FLOPS'.format(ops, res, Dt, (ops / Dt)))


def plotDemo():
    """Plot graph of approximations to Pi"""

    pi_true = FixedPoint.FXfamily(200).GetPi()
    datlist = []
    for res in range(10,26):
        val = 4 * FixedPoint.FXnum(1, FixedPoint.FXfamily(res)).atan()
        datlist.append([res, val])
    trulist = [[10, pi_true], [25, pi_true]]

    PostScript = False
    fig = Gnuplot.Gnuplot()
    fig('set xlabel "bits"')
    fig('set ylabel "4 tan^{-1}1"')
    fig('set xrange [10:25]')
    fig('set autoscale y')
    fig('set data style linespoints')
    fig('set grid')
    plitems = []
    plitems.append(Gnuplot.Data(Numeric.array(trulist, 'f')))
    plitems.append(Gnuplot.Data(Numeric.array(datlist, 'f')))
    fig._add_to_queue(plitems)
    fig.refresh()
    if PostScript:
        fig.hardcopy('/tmp/graph.ps', terminal='postscript', eps=True, enhanced=True, color=True, solid=True, fontsize=20)
    input('hit return to continue...')


if __name__ == "__main__":
    basicDemo()
    overflowDemo()
    speedDemo()
    try:
        import Gnuplot, Numeric
        plotDemo()
    except ImportError: pass

# vim: set ts=4 sw=4 et:
