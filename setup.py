#!/usr/bin/python
# installation/setup script for Simple Python Fixed-Point Module
# $Revision$, $Date$
# RW Penney, January 2007

from distutils.core import setup

setup(
    author = 'RW Penney',
    author_email = 'rwpenney@users.sourceforge.net',
    description = 'tools for arithmetic on fixed-point (binary) numbers',
    fullname = 'Simple Python Fixed-Point Module',
    keywords = 'arithmetic, fixed-point, trigonometry, arbitrary precision',
    license = 'PSF Python License',
    long_description = \
    	'FixedPoint (SPFPM) is a pure-Python module which provides ' + \
	'basic facilities for manipulating fixed-point numbers ' + \
	'of essentially arbitrary precision. ' + \
	'It aims to be more suitable for simulating binary ' + \
	'fixed-point artihmetic within electronic hardware ' + \
	'(e.g. for digital signal processing (DSP) applications) ' + \
	'than the Decimal package, which is more concerned ' + \
	'with fixed-point arithmetic in base-10. ' + \
	'SPFPM supports basic arithmetic operations as well as a range ' + \
	'of mathematical functions including sqrt, exp, sin, cos, atan etc.',
    name = 'spfpm',
    url = 'http://www.sourceforge.net/projects/pyfixedpoint',
    version = '0.6.1',
    py_modules = [ 'FixedPoint' ])
