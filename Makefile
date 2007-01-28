# Makefile for Simple Python Fixed-Point Module
# $Revision$, $Date$
# RW Penney, January 2007

VERSION=	0.4

.PHONY:	dist-zip
dist-zip:
	mkdir spfpm-${VERSION}
	tar -cf - `cat distfiles` | ( cd spfpm-${VERSION}; tar -xpf - )
	zip -r spfpm-${VERSION}.zip ./spfpm-${VERSION}
	rm -rf spfpm-${VERSION}
