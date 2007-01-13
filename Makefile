# Makefile for Simple Python Fixed-Point Module
# $Revision$, $Date$
# RW Penney, January 2007

VERSION=	0.2

.PHONY:	dist-gzip
dist-gzip:
	mkdir spfpm-${VERSION}
	tar -cf - `cat distfiles` | ( cd spfpm-${VERSION}; tar -xpf - )
	tar -zcf spfpm-${VERSION}.tar.gz ./spfpm-${VERSION}
	rm -rf spfpm-${VERSION}
