#!/usr/bin/python
# Graphical demo of Simply Python Fixed-Point Module
# RW Penney, January 2007

from FixedPoint import *
import Gnuplot, Numeric, optparse

def DoPlot(func, samples=range(10,26), label='function',
            error=False, postscript=False, filename='/tmp/graph.ps'):
    fam_acc = FXfamily(100 + samples[-1])
    val_true = func(fam_acc)
    datlist = []
    for res in samples:
        fam = FXfamily(res)
        val = func(fam)
        if error:
            eps = (FXnum(val, fam_acc) - val_true)
            disc = (abs(eps)).log() / fam_acc.GetLog2() + res
            datlist.append([res, disc])
        else:
            datlist.append([res, val])
    trulist = [[samples[0], val_true], [samples[-1], val_true]]

    fig = Gnuplot.Gnuplot()
    fig('set xlabel "bits"')
    fig('set ylabel "' + label + '"')
    fig('set xrange [' + str(samples[0]) + ':' + str(samples[-1]) + ']')
    fig('set autoscale y')
    fig('set data style linespoints')
    fig('set grid')
    if error:
        plitems = [Gnuplot.Data(Numeric.array(datlist, 'f'))]
    else:
        plitems = [Gnuplot.Data(Numeric.array(trulist, 'f')), \
                    Gnuplot.Data(Numeric.array(datlist, 'f'))]
    fig._add_to_queue(plitems)
    fig.refresh()

    if postscript:
        fig.hardcopy(filename, terminal='postscript', eps=True, enhanced=True, color=True, solid=True, fontsize=20)
    else:
        input('Hit return to continue...')



if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-e', '--errors', default=False, action='store_true')
    parser.add_option('-p', '--postscript', default=False, action='store_true')
    opts, args = parser.parse_args()

    gconfig = [
        ( lambda fam: 4 * FXnum(1, fam). atan(),
            range(10, 26), '4 tan^{-1}1', '/tmp/graph-pi.ps' ),
        ( lambda fam: (0.5 * FXnum(2, fam).log()).exp(),
            range(5, 21), 'e^{(ln 2) / 2}', '/tmp/graph-rt2.ps' )
    ]

    for cfg in gconfig:
        ( func, rng, lbl, fnm) = cfg
        if opts.errors:
            rng = range(5, 500, 10)
            lbl = 'lost-bits(' + lbl + ')'
        DoPlot(func, samples=rng, label=lbl, error=opts.errors, postscript=opts.postscript, filename=fnm)

# vim: set ts=4 sw=4 et:
