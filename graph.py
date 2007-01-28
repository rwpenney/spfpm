#!/usr/bin/python
# graphical demo of Simply Python Fixed-Point Module
# $Revision$, $Date$
# RW Penney, January 2007

import FixedPoint, Gnuplot, Numeric

pi_true = FixedPoint.FXfamily(200).GetPi()
datlist = []
for res in range(10,25):
    val = 4 * FixedPoint.FXnum(1, FixedPoint.FXfamily(res)).atan()
    datlist.append([res, val])
trulist = [[10, pi_true], [25, pi_true]]

PostScript = True
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
