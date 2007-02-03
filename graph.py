#!/usr/bin/python
# graphical demo of Simply Python Fixed-Point Module
# $Revision$, $Date$
# RW Penney, January 2007

from FixedPoint import *
import Gnuplot, Numeric

def DoPlot(func, samples=range(10,26), label='function', postscript=False, filename='/tmp/graph.ps'):
    fam = FXfamily(100 + samples[-1])
    val_true = func(fam)
    datlist = []
    for res in samples:
        fam = FXfamily(res)
        val = func(fam)
        datlist.append([res, val])
    trulist = [[samples[0], val_true], [samples[-1], val_true]]

    fig = Gnuplot.Gnuplot()
    fig('set xlabel "bits"')
    fig('set ylabel "' + label + '"')
    fig('set xrange [' + str(samples[0]) + ':' + str(samples[-1]) + ']')
    fig('set autoscale y')
    fig('set data style linespoints')
    fig('set grid')
    plitems = [Gnuplot.Data(Numeric.array(trulist, 'f')), \
                Gnuplot.Data(Numeric.array(datlist, 'f'))]
    fig._add_to_queue(plitems)
    fig.refresh()

    if postscript:
        fig.hardcopy(filename, terminal='postscript', eps=True, enhanced=True, color=True, solid=True, fontsize=20)
    else:
        raw_input('hit return to continue...')



if __name__ == "__main__":
    func = lambda fam: 4 * FXnum(1, fam).atan()
    DoPlot(func, samples=range(10,26), label='4 tan^{-1}1')

    func = lambda fam: (0.5 * FXnum(2, fam).log()).exp()
    DoPlot(func, samples=range(5,21), label='e^{(ln 2) / 2}')

