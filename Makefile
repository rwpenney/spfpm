# Makefile for Simple Python Fixed-Point Module
# RW Penney, January 2007

PYTHON=		python3
TEMPDIRS=	build dist
TEMPFILES=	MANIFEST

.PHONY:	demo
demo:
	${PYTHON} demo.py

.PHONY:	test
test:
	${PYTHON} FixedPoint.py
	(cd tests; ${PYTHON} testFixedPoint.py)

.PHONY:	clean
clean:
	for dir in ${TEMPDIRS}; do test -d $${dir} && rm -rf $${dir}; done
	for fl in ${TEMPFILES}; do test -f $${fl} && rm -f $${fl}; done
