#!/usr/bin/python
# simple approximation to pi, based on atan(1/sqrt(3))
# $Revision$, $Date$
# RW Penney, December 2006

import math

terms = 15


def six():
    scl = 2 * math.sqrt(3)
    sum = 1.0
    fac = 4.0 / 9.0
    idx = 1
    while idx < terms:
        sum -= fac * (2 * idx + 1.0) / (16 * idx * idx - 1.0)
        fac /= 9.0
        idx += 1
        print(sum * scl, '   ', math.sin(sum * scl))

def eight():
    rt2 = math.sqrt(2)
    scl = 8 * math.sqrt((rt2 - 1) / (rt2 + 1))
    sum = 1.0
    fac = 1.0
    idx = 1
    while idx < terms:
        fac *= (3 - 2 * rt2) / (3 + 2 * rt2)
        sum -= fac * (8 * idx + 2 * rt2) /   \
                ((rt2 - 1.0) * (16 * idx * idx - 1.0))
        idx += 1
        print(sum * scl, '   ', math.sin(sum * scl))

def main():
    six()
    print()
    eight()

if __name__ == "__main__":
    main()
