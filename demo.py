#!/usr/bin/python
# demonstration of Simple Python Fixed-Point Module
# $Revision$, $Date$
# Copyright 2006-2007, RW Penney


import FixedPoint

def basicDemo():
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


def plotDemo():
    # plot graph of approximations to Pi
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
    raw_input('hit return to continue...')


if __name__ == "__main__":
    basicDemo()
    try:
        import Gnuplot, Numeric
        plotDemo()
    except ImportError: pass
