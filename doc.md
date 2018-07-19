# User Documentation for the IMath Library

M. J. Fromberger <michael.j.fromberger+imath@gmail.com>

> Disclaimer: This document was converted fairly naively to Markdown from the
> original IMath doc.txt file. The API documentation should still be correct,
> but the build instructions are somewhat ridiculous at this point. I'll try to
> clean it up as time allows.

## Installation

1. Edit Makefile to select compiler and options.  The default uses gcc.  If you
   are building under MacOS 10.1.x, you will need to change CC to `cc` instead
   of `gcc`, but otherwise you can use the default GCC settings.
 
   By default, the Makefile assumes you can use the "long long" integer type,
   even though it is not standard in ANSI C90.  You can control this by setting
   the USELLONG variable in your make command line.  Setting USELLONG=Y enables
   "long long"; USELLONG=N disables it.  The default is Y.

   If the built-in types do not work for your particular platform, you can try
   to find suitable integer type sizes by running the Python program
   `findsizes.py`.  This requires a Python interpreter, version 2.4.x or later.

2. Type `make` or `make test` to build the test driver and run the unit tests.
   None of these should fail.  If they do, see below for how you can report
   bugs.

   To build with debugging enabled (and optimization disabled), run `make
   DEBUG=Y`.  This sets the preprocessor macro `DEBUG` to 1, and several other
   things (see Makefile for details).

To use the library in your code, include "imath.h" wherever you intend to use
the library's routines.  The integer library is just a single source file, so
you can compile it into your project in whatever way makes sense.  If you wish
to use rational arithmetic, you will also need to include "imrat.h".

## Background

The basic types defined by the imath library are `mpz_t`, an arbitrary
precision signed integer, and `mpq_t`, an arbitrary precision signed rational
number.  The type `mp_int` is a pointer to an `mpz_t`, and `mp_rat` is a
pointer to an `mpq_t`.

Most of the functions in the imath library return a value of type `mp_result`.
This is a signed integer type which can be used to convey status information
and also return small values.  Any negative value is considered to be a status
message.  The following constants are defined for processing these:

| Status      | Description                                  |
| ----------- | -------------------------------------------- |
| `MP_OK`     | operation successful, all is well (= 0)      |
| `MP_FALSE`  | boolean false (= `MP_OK`)                    |
| `MP_TRUE`   | boolean true                                 |
| `MP_MEMORY` | out of memory                                |
| `MP_RANGE`  | parameter out of range                       |
| `MP_UNDEF`  | result is undefined (e.g., division by zero) |
| `MP_TRUNC`  | output value was truncated                   |
| `MP_BADARG` | an invalid parameter was passed              |

If you obtain a zero or negative value of an `mp_result`, you can use the
`mp_int_error_string()` routine to obtain a pointer to a brief human-readable
string describing the error.  These strings are statically allocated, so they
need not be freed by the caller; the same strings are re-used from call to
call.

Unless otherwise noted, it is legal to use the same parameter for both inputs
and output with most of the functions in this library.  For example, you can
add a number to itself and replace the original by writing:

    mp_int_add(a, a, a);  /* a = a + a */

Any cases in which this is not legal will be noted in the function summaries
below (if you discover that this is not so, please report it as a bug; I will
fix either the function or the documentation :)

## The IMath API

Each of the API functions is documented here.  The general format of the
entries is:

```
return_type function_name(parameters ...)
            English description.
```
			
Unless otherwise noted, any API function that returns `mp_result` may be
expected to return `MP_OK`, `MP_BADARG`, or `MP_MEMORY`.  Other return values
should be documented in the description.  Please let me know if you discover
this is not the case.

The following macros are defined in "imath.h", to define the sizes of the
various data types used in the library:

| Constant        | Description
| --------------- | ----------------------------------------
| `MP_DIGIT_BIT`  | the number of bits in a single `mpz_t` digit.
| `MP_WORD_BIT`   | the number of bits in a `mpz_t` word.
| `MP_SMALL_MIN`  | the minimum value representable by an `mp_small`.
| `MP_SMALL_MAX`  | the maximum value representable by an `mp_small`.
| `MP_USMALL_MIN` | the minimum value representable by an `mp_usmall`.
| `MP_USMALL_MAX` | the maximum value representable by an `mp_usmall`.
| `MP_MIN_RADIX`  | the minimum radix accepted for base conversion.
| `MP_MAX_RADIX`  | the maximum radix accepted for base conversion.

An `mp_int` must be initialized before use.  This may be accomplished using the
following functions:

```
mp_result mp_int_init(mp_int z);
          Initializes z with a default precision, sets the value to zero.  This
          function cannot fail unless z is NULL.

mp_int    mp_int_alloc();
          Dynamically allocates an mpz_t, initializes it to the value zero, and
          returns a pointer to it.  Returns NULL in case of error (the only
          error possible is MP_MEMORY in this case).

mp_result mp_int_init_size(mp_int z, mp_size prec);
          Initializes z with at least prec digits of storage, sets the value to
          zero.  If prec is zero, the default size is used, defined in imath.h
          as MP_DEFAULT_PREC.  The size is rounded up to the nearest word
          boundary.

mp_result mp_int_init_copy(mp_int z, mp_int old);
          Initializes z to be a copy of an already-initialized mp_int in old.
          They do not share storage.

mp_result mp_int_init_value(mp_int z, mp_small value);
          Initializes z with default precision and sets its value to the value
          of the supplied integer.
```

To copy one `mp_int` to another, use:

```
mp_result mp_int_copy(mp_int a, mp_int c);
          Copies the value of a into c.  Does not allocate new memory unless a
          has more significant digits than c has room for.
```

When you are finished with an `mp_int`, you must free the memory it uses:

```
void      mp_int_clear(mp_int z);
          Releases the storage used by z.

void      mp_int_free(mp_int z);
          Releases the storage used by z, and frees the mpz_t structure z
          points to.  This should only be used for values allocated by
          mp_int_alloc().
```

To set an `mp_int`, which has already been initialized, to a small integer
value, use the following:

```
mp_result mp_int_set_value(mp_int z, mp_small value);
          Sets the value of z to the value of the supplied integer.
```

By default, an `mp_int` is initialized with a certain minimum amount of storage
for digits.  This storage is expanded automatically as needed.

### Arithmetic Functions

```
int       mp_int_is_odd(mp_int z);
          Returns true if z is an odd integer (z = 1 (mod 2))
          [currently implemented as a macro]

int       mp_int_is_even(mp_int z);
          Returns true if z is an even integer (z = 0 (mod 2))
          [currently implemented as a macro]

void      mp_int_zero(mp_int z);
          Sets z to zero.

mp_result mp_int_abs(mp_int a, mp_int c);
          Sets c to the absolute value of a. 
          If a < 0, c = -a, else c = a.

mp_result mp_int_neg(mp_int a, mp_int c);
          Sets c to be the additive inverse of a, c = -a.

mp_result mp_int_add(mp_int a, mp_int b, mp_int c);
          Computes c = a + b.

mp_result mp_int_add_value(mp_int a, mp_small value, mp_int c);
          Computes c = a + value, where value is a small integer.

mp_result mp_int_sub(mp_int a, mp_int b, mp_int c);
          Computes c = a - b.

mp_result mp_int_sub_value(mp_int a, mp_small value, mp_int c);
          Computes c = a - value, where value is a small integer.

mp_result mp_int_mul(mp_int a, mp_int b, mp_int c);
          Computes c = a * b

mp_result mp_int_mul_value(mp_int a, mp_small value, mp_int c);
          Computes c = a * value, where value is a small integer.

mp_result mp_int_mul_pow2(mp_int a, mp_small p2, mp_int c);
          Computes c = a * 2^p2, where p2 >= 0.

mp_result mp_int_sqr(mp_int a, mp_int c);
          Computes c = a * a.  Faster than using mp_int_mul(a, a, c).

mp_result mp_int_root(mp_int a, mp_small b, mp_int c);
          Computes c = floor(a^{1/b}).  Returns MP_UNDEF if the root is
          undefined, i.e., if a < 0 and b is even.  Uses Newton's method to
          obtain the root.

mp_result mp_int_sqrt(mp_int a, mp_int c);
          Computes c = floor(sqrt(a)) if a >= 0.  Returns MP_UNDEF if
          a < 0.
          [currently implemented as a macro]

mp_result mp_int_div(mp_int a, mp_int b, mp_int q, mp_int r);
          Computes q, r such that a = bq + r and 0 <= r < b.

          Pass NULL for q or r if you don't need its value.  Detects and
          handles division by powers of two in an efficient manner.  Returns
          MP_UNDEF if b = 0.  If both q and r point to the same non-NULL
          location, their values on output will be arbitrary (usually
          incorrect).

mp_result mp_int_div_value(mp_int a, mp_small v, mp_int q, mp_small *r);
          Computes q, r such that a = qv + r and 0 <= r < v, where v is a small
          integer.  Pass NULL for q or r if you don't need its value.

mp_result mp_int_div_pow2(mp_int a, mp_small p2, mp_int q, mp_int r);
          Computes q, r such that a = q * 2^p2 + r.  This is a special case for
          division by powers of two that is much more efficient than using the
          regular division algorithm.  Note that mp_int_div() will
          automatically handle this case if b = 2^k for some k >= 0;
          mp_int_div_pow2() is for when you have only the exponent, not the
          expanded value.

mp_result mp_int_mod(mp_int a, mp_int m, mp_int c);
          Computes the least non-negative residue of a (mod m), and assigns the
          result to c.

mp_result mp_int_mod_value(mp_int a, mp_int value, mp_small *r);
          Computes the least non-negative residue of a (mod value), where value
          is a small integer, and assigns the result to r.

mp_result mp_int_expt(mp_int a, mp_small b, mp_int c);
          Raises a to the b power, and assigns the result to c.  It is an error
          if b < 0.

mp_result mp_int_expt_value(mp_small a, mp_small b, mp_int c);
          Raises a to the b power, and assigns the result to c.  It is an error
          if b < 0.

mp_result mp_int_expt_full(mp_int a, mp_int b, mp_int c);
          Raises a to the b power, and assigns the result to c.  It is an error
          if b < 0.
```

### Comparison Functions

Unless otherwise specified, comparison between values x and y returns a value <
0 if x is less than y, = 0 if x is equal to y, and > 0 if x is greater than y.

```
int       mp_int_compare(mp_int a, mp_int b);
          Signed comparison of a and b.

int       mp_int_compare_unsigned(mp_int a, mp_int b);
          Unsigned (magnitude) comparison of a and b.  The signs of a and b are
          not modified.

int       mp_int_compare_zero(mp_int z);
          Compare z to zero.

int       mp_int_compare_value(mp_int z, mp_small value);
int       mp_int_compare_uvalue(mp_int z, mp_usmall value);
          Compare z to small signed (value) or unsigned (uvalue) integer value.

int       mp_int_divisible_value(mp_int a, mp_small v);
          Returns true (nonzero) if a is divisible by small integer v,
          otherwise false (zero)

int       mp_int_is_pow2(mp_int z);
          Returns k >= 0 such that z = 2^k, if such a k exists; otherwise a
          value < 0 is returned.
```

### Other Useful Functions

```
mp_result mp_int_exptmod(mp_int a, mp_int b, mp_int m, mp_int c);
          Efficiently computes c = a^b (mod m).
          Returns MP_UNDEF if m = 0; returns MP_RANGE if b < 0.

mp_result mp_int_exptmod_evalue(mp_int a, mp_small v, mp_int m, mp_int c);
          Efficiently computes c = a^v (mod m).
mp_result mp_int_exptmod_bvalue(mp_small v, mp_int b, mp_int m, mp_int c);
          Efficiently computes c = v^b (mod m).

          Note: These routines use Barrett's algorithm for modular reduction.
          It is widely held (probably correctly) that using Peter Montgomery's
          multiplication algorithm would make this operation faster; but that
          algorithm has the restriction that a and m must be coprime, so I have
          not implemented it here.

mp_result mp_int_exptmod_known(mp_int a, mp_int b, mp_int m, mp_int mu, 
                               mp_int c);
          Efficiently computes c = a^b (mod m), given a precomputed reduction
          constant mu, as defined for Barrett's modular reduction algorithm.
          Returns MP_UNDEF if m = 0; returns MP_RANGE if b < 0.

mp_result mp_int_redux_const(mp_int m, mp_int c);
          Computes reduction constant mu for Barrett reduction by modulus m,
          stores the result in c.

mp_result mp_int_invmod(mp_int a, mp_int m, mp_int c);
          Computes the modular inverse of a (mod m), if it exists, and assigns
          the result to c.  Returns the least non-negative representative of
          the congruence class (mod m) containing this inverse.  Returns
          MP_UNDEF if the inverse does not exist; returns MP_RANGE if a = 0 or
          m <= 0.

mp_result mp_int_gcd(mp_int a, mp_int b, mp_int c);
          Compute the greatest common divisor if a and b, and assign the result
          to c.  Returns MP_UNDEF if the GCD is not defined (e.g., if a = 0 and
          b = 0).

mp_result mp_int_egcd(mp_int a, mp_int b, mp_int c, mp_int x, mp_int y);
          Compute the greatest common divisor of a and b, and assign the result
          to c.  Also computes x and y satisfying Bezout's identity, namely (a,
          b) = ax + by.  Returns MP_UNDEF if the GCD is not defined (e.g., if a
          = b = 0).

mp_result mp_int_lcm(mp_int a, mp_int b, mp_int c)
          Compute the least common multiple of a and b, and assign the result
          to c.  Returns MP_UNDEF if the LCM is not defined (e.g., if a = 0 and
          b = 0).

- Conversion of values:

mp_result mp_int_to_int(mp_int z, mp_small *out);
          Convert z to an int type, if it is representable as such.  Returns
          MP_RANGE if z cannot be represented as an value of type mp_small.  If
          out is NULL no value is stored, but the return value will still be
          correct.

mp_result mp_int_to_uint(mp_int z, mp_usmall *out);
          Convert z to an unsigned int type, if it is representable as such.
          Returns MP_RANGE if z cannot be represented as a value of type
          mp_usmall.  If out is NULL no value is stored, but the return value
          will still be correct.

mp_result mp_int_to_string(mp_int z, mp_size radix, char *str, int limit);
          Convert z to a zero-terminated string of characters in the given
          radix, writing at most 'limit' characters including the terminating
          NUL value.  A leading '-' is used to indicate a negative value.

          Returns MP_RANGE if radix < MP_MIN_RADIX or radix > MP_MAX_RADIX.
          Returns MP_TRUNC if limit is too small to write out all of z.

mp_result mp_int_string_len(mp_int z, mp_size radix);
          Return the minimum number of characters required to represent z as a
          zero-terminated string of characters in the given radix. May
          over-estimate (but generally will not).

          Returns MP_RANGE if radix < MP_MIN_RADIX or radix > MP_MAX_RADIX.

mp_result mp_int_read_string(mp_int z, mp_size radix, const char *str);
mp_result mp_int_read_cstring(mp_int z, mp_size radix, const char *str, 
                              char **end);
          Read a string of ASCII digits in the specified radix from the
          zero-terminated string provided, and assign z to the corresponding
          value.  For radices greater than 10, the ASCII letters 'A' .. 'Z' or
          'a' .. 'z' are used.  Letters are interpreted without respect to
          case.

          Leading whitespace is ignored, and a leading '+' or '-' is
          interpreted as a sign flag.  Processing stops when ASCII NUL or any
          character which is out of range for a digit in the given radix is
          encountered.

          If the whole string was processed, MP_OK is returned; otherwise,
          MP_TRUNC is returned.

          Returns MP_RANGE if radix < MP_MIN_RADIX or radix > MP_MAX_RADIX.

          With mp_int_read_cstring(), if end is not NULL, the target pointer is
          set to point to the first unconsumed character of the input string
          (the NUL byte, if the whole string was consumed).  This emulates the
          behavior of the standard C strtol() function.

mp_result mp_int_count_bits(mp_int z);
          Returns the number of significant bits in z.

mp_result mp_int_to_binary(mp_int z, unsigned char *buf, int limit);
          Convert z to 2's complement binary, writing at most 'limit' bytes
          into the given buffer.  Returns MP_TRUNC if the buffer limit was too
          small to contain the whole value.  If this occurs, the contents of
          buf will be effectively garbage, as the function uses the buffer as
          scratch space.

          The binary representation of z is in base-256 with digits ordered
          from most significant to least significant (network byte ordering).
          The high-order bit of the first byte is set for negative values,
          clear for non-negative values.

          As a result, non-negative values will be padded with a leading zero
          byte if the high-order byte of the base-256 magnitude is set.  This
          extra byte is accounted for by the mp_int_binary_len() function
          described below.

mp_result mp_int_read_binary(mp_int z, unsigned char *buf, int len);
          Read a 2's complement binary value into z, where the length of the
          buffer is given as 'len'.  The contents of 'buf' may be overwritten
          during processing, although they will be restored when the function
          returns.

mp_result mp_int_binary_len(mp_int z);
          Return the number of bytes required to represent z in 2's complement
          binary.

mp_result mp_int_to_unsigned(mp_int z, unsigned char *buf, int limit);
          Convert |z| to unsigned binary, writing at most 'limit' bytes into
          the given buffer.  The sign of z is ignored, but z is not modified.
          Returns MP_TRUNC if the buffer limit was too small to contain the
          whole value.  If this occurs, the contents of buf will be effectively
          garbage, as the function uses the buffer as scratch space during
          conversion.

          The binary representation of z is in base-256 with digits ordered
          from most significant to least significant (network byte ordering).

mp_result mp_int_read_unsigned(mp_int z, unsigned char *buf, int len);
          Read an unsigned binary value into z, where the length of the buffer
          is given as 'len'.  The contents of 'buf' will not be modified during
          processing.

mp_result mp_int_unsigned_len(mp_int z);
          Return the number of bytes required to represent z as an unsigned
          binary value using mp_int_to_unsigned().
```

### Other Functions

Ordinarily, integer multiplication and squaring are done using the simple
quadratic "schoolbook" algorithm.  However, for sufficiently large values,
there is a more efficient algorithm usually attributed to Karatsuba and Ofman
that is usually faster.  See Knuth Vol. 2 for more details about how this
algorithm works.

The breakpoint between the "normal" and the recursive algorithm is controlled
by a static constant `multiply_threshold` defined in imath.c, which contains
the number of significant digits below which the standard algorithm should be
used.  This is initialized to the value of the compile-time constant
`MP_MULT_THRESH` from imath.h.  If you wish to be able to modify this value at
runtime, compile imath.c with `IMATH_TEST` defined true in the preprocessor,
and declare

    extern mp_size multiply_threshold;

When `IMATH_TEST` is defined, this variable is defined as a mutable global, and
can be changed.  Otherwise, it is defined as an immutable static constant.  The
`imtimer` program and the `findthreshold.py` script (Python) can help you find
a suitable value for `MP_MULT_THRESH` for your particular platform.

```
const char *mp_int_error_string(mp_result res);
          Return a pointer to a brief string describing 'res'.  These strings
          are defined as a constant array in `imath.c', if you wish to change
          them for your application.
```

## Rational Arithmetic

```
mp_result mp_rat_init(mp_rat r);
          Initialize a new zero-valued rational number in r.

mp_result mp_rat_init_size(mp_rat r, mp_size n_prec, mp_size d_prec);
          As mp_rat_init(), but specifies the number of long digits of
          precision for numerator (n_prec) and denominator (d_prec).  Use this
          if you wish to preallocate storage for operations of known output
          size.

mp_result mp_rat_init_copy(mp_rat r, mp_rat old);
          As mp_rat_init(), but initializes a copy of an existing rational
          value.

mp_result mp_rat_set_value(mp_rat r, mp_small numer, mp_small denom);
          Set the value of the given rational to a ratio specified as ordinary
          signed integers (denom != 0).  Returns MP_UNDEF if denom = 0.

void      mp_rat_clear(mp_rat r);
          Release the memory occupied by the given rational number.

mp_result mp_rat_numer(mp_rat r, mp_int z);
          Extract the numerator of r as an mp_int, and store it in z.

mp_result mp_rat_denom(mp_rat r, mp_int z);
          Extract the denominator of r as an mp_int, and store it in z.

mp_sign   mp_rat_sign(mp_rat r);
          Return the sign of the rational number.  Note that an mpq_t
          is always stored so that the sign of the numerator is the
          correct sign of the whole value.

mp_result mp_rat_copy(mp_rat a, mp_rat c);
          Copy a to c.  Avoids unnecessary allocations.

void      mp_rat_zero(mp_rat r);
          Set r to have the value zero (canonical with denominator 1).

mp_result mp_rat_abs(mp_rat a, mp_rat c);
          Set c to the absolute value of a.

mp_result mp_rat_neg(mp_rat a, mp_rat c);
          Set c to the negative (additive inverse) of a.

mp_result mp_rat_recip(mp_rat a, mp_rat c);
          Take the reciprocal of a and store it in c, if defined.
          Returns MP_UNDEF if a/c = 0.

mp_result mp_rat_add(mp_rat a, mp_rat b, mp_rat c);
          Add a + b and store the result in c.

mp_result mp_rat_sub(mp_rat a, mp_rat b, mp_rat c);
          Subtract a - b and store the result in c.

mp_result mp_rat_mul(mp_rat a, mp_rat b, mp_rat c);
          Multiply a * b and store the result in c.

mp_result mp_rat_div(mp_rat a, mp_rat b, mp_rat c);
          Divide a / b, if possible, and store the result in c.
          Returns MP_UNDEF if b = 0.

mp_result mp_rat_add_int(mp_rat a, mp_int b, mp_rat c);
          Add a + b and store the result in c.  Note:  b is an integer.

mp_result mp_rat_sub_int(mp_rat a, mp_int b, mp_rat c);
          Subtract a - b and store the result in c.  Note:  b is an integer.

mp_result mp_rat_mul_int(mp_rat a, mp_int b, mp_rat c);
          Multiply a * b and store the result in c.  Note:  b is an integer.

mp_result mp_rat_div_int(mp_rat a, mp_int b, mp_rat c);
          Divide a / b, if possible, and store the result in c.
          Note:  b is an integer.
          Returns MP_UNDEF if b = 0.

mp_result mp_rat_expt(mp_rat a, mp_small b, mp_rat c);
          Raise a to the b power, where b >= 0, and store the result in c.

int       mp_rat_compare(mp_rat a, mp_rat b);
          Full signed comparison of rational values.

int       mp_rat_compare_unsigned(mp_rat a, mp_rat b);
          Compare the absolute values of a and b.

int       mp_rat_compare_zero(mp_rat r);
          Compare r to zero.

int       mp_rat_compare_value(mp_rat r, mp_small n, mp_small d);
          Compare r to the ratio n/d.

int       mp_rat_is_integer(mp_rat r);
          Returns true if r can be represented by an integer (i.e.,
          its denominator is one).

mp_result mp_rat_to_ints(mp_rat r, mp_small *num, mp_small *den);
          If it is possible to do so, extract the numerator and the denominator
          of r as regular (signed) integers.  Returns MP_RANGE if either cannot
          be so represented.

mp_result mp_rat_to_string(mp_rat r, mp_size radix, char *str, int limit);
          Convert the value of r to a string of the format "n/d" with n and d
          in the specified radix, writing no more than "limit" bytes of data to
          the given output buffer.  Includes sign flag.

mp_result mp_rat_to_decimal(mp_rat r, mp_size radix, mp_size prec,
                            mp_round_mode rmode, char *str, int limit);
          Convert the value of r to a string in decimal-point notation with the
          specified radix, writing no more than "limit" bytes of data to the
          given output buffer.  Generates "prec" digits of precision.

          Values numbers may be rounded when they are being converted for
          output as a decimal value.  There are four rounding modes currently
          supported:

          MP_ROUND_DOWN
            Truncates the value toward zero.  
            Example:  12.009 to 2dp becomes 12.00

          MP_ROUND_UP
            Rounds the value away from zero:
            Example:  12.001 to 2dp becomes 12.01, but
                      12.000 to 2dp remains 12.00

          MP_ROUND_HALF_DOWN
             Rounds the value to nearest digit, half goes toward zero.
             Example:  12.005 to 2dp becomes 12.00, but
                       12.006 to 2dp becomes 12.01

          MP_ROUND_HALF_UP
             Rounds the value to nearest digit, half rounds upward.
             Example:  12.005 to 2dp becomes 12.01, but
                       12.004 to 2dp becomes 12.00

mp_result mp_rat_string_len(mp_rat r, mp_size radix);
          Return the length of buffer required to convert r using the
          mp_rat_to_string() function.  May over-estimate slightly.

mp_result mp_rat_decimal_len(mp_rat r, mp_size radix, mp_size prec);
          Return the length of buffer required to convert r using the
          mp_rat_to_decimal() function.  May over-estimate slightly.

mp_result mp_rat_read_string(mp_rat r, mp_size radix, char *str);
          Read a zero-terminated string in the format "n/d" (including sign
          flag), and replace the value of r with it.

mp_result mp_rat_read_cstring(mp_rat r, mp_size radix, char *str, char **end);
          Like mp_rat_read_string(), but with a similar interface to the
          strtoul() library function.  Used as the back end for the
          mp_rat_read_string() function.  Returns MP_UNDEF if the denominator
          read has value zero.

mp_result mp_rat_read_ustring(mp_rat r, mp_size radix, char *str, char **end);
          A "universal" reader.  Capable of reading plain integers, rational
          number written in a/b notation, and decimal values in z.f format.
          The end parameter works as for mp_int_read_cstring().

mp_result mp_rat_read_decimal(mp_rat r, mp_size radix, char *str);
          A wrapper around mp_rat_read_cdecimal(), which discards the resulting
          end pointer.

mp_result mp_rat_read_cdecimal(mp_rat r, mp_size radix, char *str, char **end);
          Read a zero-terminated string in the format "z.f" (including sign
          flag), and replace r with its value.  If end is not NULL, a pointer
          to the first unconsumed character of the string is returned.
```

## Representation Details

> NOTE: You do not need to read this section to use IMath.  This is provided
> for the benefit of developers wishing to extend or modify the internals of
> the library.

IMath uses a signed magnitude representation for arbitrary precision integers.
The magnitude is represented as an array of radix-R digits in increasing order
of significance; the value of R is chosen to be half the size of the largest
available unsigned integer type, so typically 16 or 32 bits.  Digits are
represented as mp_digit, which must be an unsigned integral type.

Digit arrays are allocated using `malloc(3)` and `realloc(3)`.  Because this
can be an expensive operation, the library takes pains to avoid allocation as
much as possible.  For this reason, the `mpz_t` structure distinguishes between
how many digits are allocated and how many digits are actually consumed by the
representation.  The fields of an `mpz_t` are:

    mp_digit    single;  /* single-digit value (see note) */
    mp_digit   *digits;  /* array of digits               */
    mp_size     alloc;   /* how many digits are allocated */
    mp_size     used;    /* how many digits are in use    */
    mp_sign     sign;    /* the sign of the value         */

The elements of `digits` at indices less than `used` are the significant
figures of the value; the elements at indices greater than or equal to `used`
are undefined (and may contain garbage).  At all times, `used` must be at least
1 and at most `alloc`.

To avoid interaction with the memory allocator, single-digit values are stored
directly in the `mpz_t` structure, in the `single` field.  The semantics of
access are the same as the more general case.

The number of digits allocated for an `mpz_t` is referred to in the library
documentation as its "precision".  Operations that affect an `mpz_t` cause
precision to increase as needed.  In any case, all allocations are measured in
digits, and rounded up to the nearest `mp_word` boundary.  There is a default
minimum precision stored as a static constant default_precision (imath.c); its
value is set to `MP_DEFAULT_PREC` (imath.h).  If the preprocessor symbol
`IMATH_TEST` is defined, this value becomes global and modifiable.

Note that the allocated size of an `mpz_t` can only grow; the library never
reallocates in order to decrease the size.  A simple way to do so explicitly is
to use `mp_int_init_copy()`, as in:

```
mpz_t big, new;

/* ... */
mp_int_init_copy(&new, &big);
mp_int_swap(&new, &big);
mp_int_clear(&new);
```

The value of `sign` is 0 for positive values and zero, 1 for negative values.
Constants `MP_ZPOS` and `MP_NEG` are defined for these; no other sign values
are used.

If you are adding to this library, you should be careful to preserve the
convention that inputs and outputs can overlap, as described above.  So, for
example, `mp_int_add(a, a, a)` is legal.  Often, this means you must maintain
one or more temporary mpz_t structures for intermediate values.  The private
macros `SETUP(E, C)` and `TEMP(K)` can be used to enforce a conventional
structure like this:

```
{
  mpz_t     temp[NUM_TEMPS];  /* declare how many you need here */
  int       last = 0;         /* number of in-use temps         */
  mp_result res;              /* used for checking results      */
  ...

  /* Initialization phase */ 
  SETUP(mp_int_init(TEMP(0)), last);
  SETUP(mp_int_init_copy(TEMP(1), x), last);
  ...
  SETUP(mp_int_init_value(TEMP(7), 3), last);

  /* Work phase */
  ...

CLEANUP:
  while(--last >= 0) {
    mp_int_clear(TEMP(last));
  }
  return res;
}
```

The names `temp` and `res` are fixed -- the `SETUP` and `TEMP` macros assume
they exist.  `TEMP(k)` returns a pointer to the kth entry of temp.  This
structure insures that even if a failure occurs during the "initialization
phase", no memory is leaked.

"Small" integer values are represented by the types `mp_small` and `mp_usmall`,
which are mapped to appropriately-sized types on the host system.  The default
for `mp_small` is "long" and the default for `mp_usmall` is "unsigned long".
You may change these, provided you insure that `mp_small` is signed and
`mp_usmall` is unsigned.  You will also need to adjust the size macros:

    MP_SMALL_MIN, MP_SMALL_MAX
    MP_USMALL_MIN, MP_USMALL_MAX

... which are defined in <imath.h>, if you change these.

Rational numbers are represented using a pair of arbitrary precision integers,
with the convention that the sign of the numerator is the sign of the rational
value, and that the result of any rational operation is always represented in
lowest terms.  The canonical representation for rational zero is 0/1.  See
"imrat.h".

## Testing and Reporting of Bugs

Test vectors are included in the `tests/` subdirectory of the imath
distribution.  When you run `make test`, it builds the `imtest` program and
runs all available test vectors.  If any tests fail, you will get a line like
this:

    x    y    FAILED      v

Here, _x_ is the line number of the test which failed, _y_ is index of the test
within the file, and _v_ is the value(s) actually computed.  The name of the
file is printed at the beginning of each test, so you can find out what test
vector failed by executing the following (with x, y, and v replaced by the
above values, and where "foo.t" is the name of the test file that was being
processed at the time):

    % tail +x tests/foo.t | head -1

None of the tests should fail (but see [Note 2](#note2)); if any do, it
probably indicates a bug in the library (or at the very least, some assumption
I made which I shouldn't have).  Please send a bug report to the address below,
which includes the `FAILED` test line above, as well as the output of the above
`tail` command (so I know what inputs caused the failure).

If you build with the preprocessor symbol `DEBUG` defined as a positive
integer, you will have access to several things:

 1. The static functions defined in imath.c are made globally visible so that
    you can call them from a test driver.

 2. The `s_print()` and `s_print_buf()` routines are defined; these make it
    easier to dump the contents of an `mpz_t` to text.

 3. If `DEBUG > 1`, the digit allocators (`s_alloc`, `s_realloc`) fill all new
    buffers with the value `0xDEADBEEF`, or as much of it as will fit in a
    digit, so that you can more easily catch uninitialized reads in the
    debugger.

## Notes

1. <a name="note1"></a>You can generally use the same variables for both input
   and output.  One exception is that you may not use the same variable for
   both the quotient and the remainder of `mp_int_div()`.

2. <a name="note2"></a>Many of the tests for this library were written under
   the assumption that the `mp_small` type is 32 bits or more.  If you compile
   with a smaller type, you may see `MP_RANGE` errors in some of the tests that
   otherwise pass (due to conversion failures).  Also, the pi generator (pi.c)
   will not work correctly if `mp_small` is too short, as its algorithm for arc
   tangent is fairly simple-minded.

## Contacts

The IMath library was written by Michael J. Fromberger.

If you discover any bugs or testing failures, please send e-mail to the above
address. Please be sure to include, with any bug report, a complete description
of what goes wrong, and if possible, a test vector for imtest or a minimal test
program that will demonstrate the bug on your system.  Please also let me know
what hardware, operating system, and compiler you're using.

## Acknowledgements

The algorithms used in this library came from Vol. 2 of Donald Knuth's "The Art
of Computer Programming" (Seminumerical Algorithms).  Thanks to Nelson Bolyard,
Bryan Olson, Tom St. Denis, Tushar Udeshi, and Eric Silva for excellent
feedback on earlier versions of this code.  Special thanks to Jonathan Shapiro
for some very helpful design advice, as well as feedback and some clever ideas
for improving performance in some common use cases.

## License and Disclaimers

IMath is Copyright 2002-2009 Michael J. Fromberger
You may use it subject to the following Licensing Terms:

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
