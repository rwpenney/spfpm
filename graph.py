#!/usr/bin/python3
# Graphical demo of Simply Python Fixed-Point Module
# RW Penney, January 2007

import matplotlib, numpy, optparse

matplotlib.use('qt4agg')
import matplotlib.pyplot as plt

from FixedPoint import *


def DoPlot(func, samples=range(10,26), label='function', plot_diff=False):
    fam_acc = FXfamily(32 + samples[-1])
    val_true = func(fam_acc)

    datlist = []
    for res in samples:
        fam = FXfamily(res)
        val = func(fam)

        if plot_diff:
            eps = (FXnum(val, fam_acc) - val_true)
            disc = (abs(eps)).log() / fam_acc.GetLog2() + res
            datlist.append([res, disc, val_true])
        else:
            datlist.append([res, val, val_true])

    acc = numpy.array(datlist)

    plt.xlabel('bits')
    plt.ylabel(label)
    plt.grid(True)

    if not plot_diff:
        plt.plot(acc[:,0], acc[:,2])
    plt.plot(acc[:,0], acc[:,1])
    plt.show()


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-e', '--errors', default=False, action='store_true')
    opts, args = parser.parse_args()

    gconfig = [
        ( lambda fam: 4 * FXnum(1, fam). atan(),
            range(10, 26), '$4 \\tan^{-1}1$', '/tmp/graph-pi.ps' ),
        ( lambda fam: (0.5 * FXnum(2, fam).log()).exp(),
            range(5, 21), '$e^{(\\ln 2) / 2}$', '/tmp/graph-rt2.ps' )
    ]

    for cfg in gconfig:
        ( func, rng, lbl, fnm) = cfg
        if opts.errors:
            rng = range(5, 500, 10)
            lbl = 'lost-bits(' + lbl + ')'
        DoPlot(func, samples=rng, label=lbl, plot_diff=opts.errors)

# vim: set ts=4 sw=4 et:
