#!/usr/bin/python
# simple approximation to pi, based on atan(1/sqrt(3))
# RW Penney, December 2006

import math

terms = 15


def main():
    scl = 2 * math.sqrt(3)
    sum = 1.0
    fac = 4.0 / 9.0
    idx = 1
    while idx < terms:
        sum -= fac * (2 * idx + 1.0) / (16 * idx * idx - 1.0)
        fac /= 9.0
        idx += 1
        print sum * scl


if __name__ == "__main__":
    main()
