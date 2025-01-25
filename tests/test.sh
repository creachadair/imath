#!/bin/bash
## 
## Name:     test.sh
## Purpose:  Run test suites for IMath library.
##
## Copyright (C) 2002-2007 Michael J. Fromberger. All Rights Reserved.
##

set -o pipefail

if [ ! -f ../imtest ] ; then
  echo "I can't find the imath test driver 'imtest', did you build it?"
  echo "I can't proceed with the unit tests until you do so, sorry."
  exit 2
fi

echo "-- Running all available unit tests"
if ../imtest *.tc | (grep -v 'OK'||true) ; then
    echo "ALL PASSED"
else
    echo "FAILED"
    exit 1
fi

pitest() {
    local digits="${1:?missing digits}"
    local radix="${2:?missing radix}"
    local file="${3:?missing golden file}"

    local tempfile="/tmp/pi.${digits}.${radix}.$$.txt"
    
    echo "-- Running test to compute ${digits} base-${radix} digits of pi" 1>&2
    ../pi "$digits" "$radix" | tr -d '\r\n' > "$tempfile"
    if cmp -s "$tempfile" "$file" ; then
	echo "  PASSED $digits digits"
    else
	echo "  FAILED"
	echo "Obtained:"
	cat "$tempfile"
	echo "Expected:"
	cat "$file"
    fi
    rm -f "$tempfile"
}

echo ""
if [ ! -f ../pi ] ; then
  echo "I can't find the pi computing program, did you build it?"
  echo "I can't proceed with the pi test until you do so, sorry."
  exit 1
fi

pitest 1024 10 pi1024.txt
pitest 1698 16 pi1698-16.txt
pitest 1500 10 pi1500-10.txt
pitest 4096 10 pi4096-10.txt

echo ""
echo "-- Running regression tests"

for bug in bug-qread bug-swap ; do
    ../${bug}
done

exit 0
