CFLAGS+=-fPIC -I$(IMATH_DIR) $(shell pkg-config --cflags gmp)
IMATH_DIR=../..
LDFLAGS+=-L$(IMATH_DIR) $(shell pkg-config --libs gmp) -limath

runtest: imath_test.so gmp_test.so wrappers.py random.tests
	./runtest $(TESTS)

gmp_test.c: gmp_custom_test.c genctest.py gmpapi.py
	./genctest.py gmp > $@

imath_test.c: imath_custom_test.c genctest.py gmpapi.py
	./genctest.py imath > $@

gmp_test.so: gmp_test.o
	$(CC) $(CFLAGS) $(LDFLAGS) -shared -o $@ $^

imath_test.so: imath_test.o
	$(CC) $(CFLAGS) $(LDFLAGS) -shared -L$(IMATH_DIR) -o $@ $^ -limath

wrappers.py: genpytest.py gmpapi.py
	./genpytest.py > $@

random.tests: gendata.py
	./gendata.py > $@

clean:
	rm -f -- a.out *.so *.o random.tests gmp_test.c imath_test.c wrappers.py *.pyc
	rm -rf __pycache__
