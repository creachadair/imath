##
## Name:     Makefile
## Purpose:  Makefile for imath library and associated tools
## Author:   M. J. Fromberger
##
## Copyright (C) 2002-2008 Michael J. Fromberger, All Rights Reserved.
##
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to
## deal in the Software without restriction, including without limitation the
## rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
## sell copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
## IN THE SOFTWARE.
##

# --- begin configuration section ---

## Generic settings for systems with GCC (default)
## To build with debugging, add DEBUG=Y on the "make" command line.
CC=gcc
CFLAGS+=-pedantic -Wall -Werror -Wextra -Wno-unused-parameter \
	-I. -std=c99 $(DFLAGS$(DEBUG))
#LIBS=

DFLAGS=-O3 -funroll-loops -finline-functions
DFLAGSN=$(DFLAGS)
DFLAGSY=-g -DDEBUG=1

# --- end of configuration section ---
VERS=1.24

REGRESSIONS=bug-swap
TARGETS=imtest imtimer pi bintest $(REGRESSIONS)
HDRS=imath.h imrat.h iprime.h imdrover.h rsamath.h gmp_compat.h
SRCS=$(HDRS:.h=.c) $(TARGETS:=.c)
OBJS=$(SRCS:.c=.o)
OTHER=LICENSE ChangeLog Makefile doc.md \
	findthreshold.py imath-test.scm imath.py
VPATH += examples
EXAMPLES=basecvt findprime randprime imcalc input rounding rsakey

.PHONY: all test clean distclean dist

.c.o:
	$(CC) $(CFLAGS) -c $<

all: objs examples test

objs: $(OBJS)

check: test gmp-compat-test
	@ echo "Completed running imath and gmp-compat unit tests"

test: imtest pi bug-swap
	@ echo ""
	@ echo "Running tests, you should not see any 'FAILED' lines here."
	@ echo "If you do, please see doc.txt for how to report a bug."
	@ echo ""
	(cd tests && ./test.sh)

gmp-compat-test: libimath.so
	@ echo "Running gmp-compat unit tests"
	@ echo "Printing progress after every 100,000 tests"
	make -C tests/gmp-compat-test TESTS="-p 100000 random.tests"

$(EXAMPLES):%: imath.o imrat.o iprime.o %.o
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

$(REGRESSIONS):%: imath.o %.o
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

examples: $(EXAMPLES)

libimath.so: imath.o imrat.o gmp_compat.o
	$(CC) $(CFLAGS) -dynamiclib -o $@ $^

imtest: imtest.o imath.o imrat.o imdrover.o
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

imtimer: imath.c imtimer.c
	$(CC) $(CFLAGS) -D_GNU_SOURCE -DIMATH_TEST -o $@ $^ $(LIBS)

pi: pi.o imath.o
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

rtest: rtest.o imath.o rsamath.o
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

bintest: imath.o bintest.o
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

format:
	find . -type f -name '*.h' -o -name '*.c' -print0 | \
		 xargs -0 clang-format --style=Google -i

clean:
	rm -f *.o *.pyc *~ core gmon.out tests/*~ tests/gmon.out examples/*~
	make -C tests/gmp-compat-test clean

distclean: clean
	rm -f $(TARGETS) imath-$(VERS).tar imath-$(VERS).tar.gz
	rm -f $(EXAMPLES)
	rm -f libimath.so

dist: distclean
	@ echo "Packing files for distribution"
	@ tar -cf imtemp.tar --exclude .svn \
		$(HDRS) $(SRCS) $(OTHER) tests examples
	@ mkdir imath-$(VERS)
	@ (cd imath-$(VERS) && tar -xf ../imtemp.tar)
	@ rm -f imtemp.tar
	@ tar -cvf imath-$(VERS).tar imath-$(VERS)
	@ echo "Compressing distribution file: " imath-$(VERS).tar
	@ gzip -9v imath-$(VERS).tar
	@ rm -rf imath-$(VERS)
