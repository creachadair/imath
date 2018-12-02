##
## Name:     imath.py
## Purpose:  CTypes wrapper for IMath library.
## Author:   M. J. Fromberger
## 

import ctypes, ctypes.util, functools

# Library path and object wrapper.
_path = ctypes.util.find_library('libimath.so') or 'libimath.so'
assert _path is not None, "Library path may not be None"
_lib  = ctypes.CDLL(_path, ctypes.RTLD_GLOBAL)

# Basic data types used by the rest of the library.
mp_sign   = ctypes.c_ubyte
mp_size   = ctypes.c_uint
mp_result = ctypes.c_int
mp_small  = ctypes.c_long
mp_usmall = ctypes.c_ulong
mp_digit  = ctypes.c_uint
mp_word   = ctypes.c_ulonglong
PTR       = ctypes.POINTER
c_int     = ctypes.c_int
c_byte    = ctypes.c_byte

class mpz_t (ctypes.Structure):
    _fields_ = [
        ('single', mp_digit),
        ('digits', PTR(mp_digit)),
        ('alloc',  mp_size),
        ('used',   mp_size),
        ('sign',   mp_sign),
        ]

mp_int = PTR(mpz_t)

def D(restype, name, *argtypes):
    func = getattr(_lib, name)
    func.restype = restype
    func.argtypes = argtypes
    return func

D(mp_result, 'mp_int_init', mp_int)
D(mp_int,    'mp_int_alloc')
D(mp_result, 'mp_int_init_size', mp_int, mp_size)
D(mp_result, 'mp_int_init_copy', mp_int, mp_int)
D(mp_result, 'mp_int_init_value', mp_int, mp_small)
D(mp_result, 'mp_int_set_value', mp_int, mp_small)
D(None,      'mp_int_clear', mp_int)
D(None,      'mp_int_free', mp_int)
D(mp_result, 'mp_int_copy', mp_int, mp_int)
D(None,      'mp_int_swap', mp_int, mp_int)
D(None,      'mp_int_zero', mp_int)
D(mp_result, 'mp_int_abs', mp_int, mp_int)
D(mp_result, 'mp_int_neg', mp_int, mp_int)
D(mp_result, 'mp_int_add', mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_add_value', mp_int, mp_small, mp_int)
D(mp_result, 'mp_int_sub', mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_sub_value', mp_int, mp_small, mp_int)
D(mp_result, 'mp_int_mul', mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_mul_value', mp_int, mp_small, mp_int)
D(mp_result, 'mp_int_mul_pow2', mp_int, mp_small, mp_int)
D(mp_result, 'mp_int_div', mp_int, mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_div_value', mp_int, mp_small, mp_int, PTR(mp_small))
D(mp_result, 'mp_int_div_pow2', mp_int, mp_small, mp_int, mp_int)
D(mp_result, 'mp_int_mod', mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_expt', mp_int, mp_small, mp_int)
D(mp_result, 'mp_int_expt_value', mp_small, mp_small, mp_int)
D(mp_result, 'mp_int_expt_full', mp_int, mp_int, mp_int)
D(c_int,     'mp_int_compare', mp_int, mp_int)
D(c_int,     'mp_int_compare_unsigned', mp_int, mp_int)
D(c_int,     'mp_int_compare_zero', mp_int)
D(c_int,     'mp_int_compare_value', mp_int, mp_small)
D(c_int,     'mp_int_compare_uvalue', mp_int, mp_usmall)
D(c_int,     'mp_int_divisible_value', mp_int, mp_small)
D(c_int,     'mp_int_is_pow2', mp_int)
D(mp_result, 'mp_int_exptmod', mp_int, mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_exptmod_evalue', mp_int, mp_small, mp_int, mp_int)
D(mp_result, 'mp_int_exptmod_bvalue', mp_small, mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_exptmod_known', mp_int, mp_int, mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_redux_const', mp_int, mp_int)
D(mp_result, 'mp_int_invmod', mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_gcd', mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_egcd', mp_int, mp_int, mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_lcm', mp_int, mp_int, mp_int)
D(mp_result, 'mp_int_root', mp_int, mp_small, mp_int)
D(mp_result, 'mp_int_to_int', mp_int, PTR(mp_small))
D(mp_result, 'mp_int_to_uint', mp_int, PTR(mp_usmall))
D(mp_result, 'mp_int_to_string', mp_int, mp_size, PTR(c_byte), c_int)
D(mp_result, 'mp_int_string_len', mp_int, mp_size)
D(mp_result, 'mp_int_read_string', mp_int, mp_size, PTR(c_byte))
D(mp_result, 'mp_int_read_cstring', mp_int, mp_size, PTR(c_byte), PTR(PTR(c_byte)))
D(mp_result, 'mp_int_count_bits', mp_int)
D(mp_result, 'mp_int_to_binary', mp_int, PTR(c_byte), c_int)
D(mp_result, 'mp_int_read_binary', mp_int, PTR(c_byte), c_int)
D(mp_result, 'mp_int_binary_len', mp_int)
D(mp_result, 'mp_int_to_unsigned', mp_int, PTR(c_byte), c_int)
D(mp_result, 'mp_int_read_unsigned', mp_int, PTR(c_byte), c_int)
D(mp_result, 'mp_int_unsigned_len', mp_int)
D(PTR(c_byte), 'mp_error_string', mp_result)

def V(restype, name):
    return restype.in_dll(_lib, name).value

MP_OK     = V(mp_result, 'MP_OK')
MP_FALSE  = V(mp_result, 'MP_FALSE')
MP_TRUE   = V(mp_result, 'MP_TRUE')
MP_MEMORY = V(mp_result, 'MP_MEMORY')
MP_RANGE  = V(mp_result, 'MP_RANGE')
MP_UNDEF  = V(mp_result, 'MP_UNDEF')
MP_TRUNC  = V(mp_result, 'MP_TRUNC')
MP_BADARG = V(mp_result, 'MP_BADARG')

class imath_error (Exception):
    pass

def check(expected, value):
    ok = ((hasattr(expected, '__call__') and expected(value))
          or expected == value)
    if not ok:
        msg = ctypes.string_at(_lib.mp_error_string(value))
        raise imath_error(msg, value)
    return value

def check_ok(value):
    return check(MP_OK, value)

def check_value(value):
    return check(lambda v: v >= 0, value)

class mpz (mpz_t):
    def __init__(self, value = None):
        super(mpz_t, self).__init__()
        if isinstance(value, mpz):
            check_ok(_lib.mp_int_init_copy(self, value))
        elif isinstance(value, int):
            check_ok(_lib.mp_int_init_value(self, value))
        elif value is not None:
            raise TypeError("unsupported initializer type")
        else:
            check_ok(_lib.mp_int_init(self))

    def __del__(self):
        _lib.mp_int_clear(self)

    @classmethod
    def from_string(cls, s, radix = 10):
        out = cls()
        buf = ctypes.create_string_buffer(s)
        ptr = ctypes.cast(buf, PTR(c_byte))
        check_ok(_lib.mp_int_read_string(out, radix, ptr))
        return out

    def to_string(self, radix = 10):
        size = check_value(_lib.mp_int_string_len(self, radix))
        buf  = ctypes.create_string_buffer(size)
        ptr  = ctypes.cast(buf, PTR(c_byte))
        check_ok(_lib.mp_int_to_string(self, radix, ptr, size))
        return buf.value

    def __neg__(self):
        t = mpz(self)
        check_ok(_lib.mp_int_neg(self, t))
        return t

    def __sbs__(self):
        t = mpz(self)
        check_ok(_lib.mp_int_abs(self, t))
        return t

    def __add__(self, other):
        t = mpz(); check_ok(_lib.mp_int_add(self, other, t)); return t

    def __iadd__(self, other):
        check_ok(_lib.mp_int_add(self, other, self))
        return self

    def __sub__(self, other):
        t = mpz(); check_ok(_lib.mp_int_sub(self, other, t)); return t

    def __isub__(self, other):
        check_ok(_lib.mp_int_sub(self, other, self))
        return self

    def __mul__(self, other):
        t = mpz(); check_ok(_lib.mp_int_mul(self, other, t)); return t

    def __imul__(self, other):
        check_ok(_lib.mp_int_mul(self, other, self))
        return self

    def __divmod__(self, other):
        q = mpz(); r = mpz()
        check_ok(_lib.mp_int_div(self, other, q, r))
        return q, r

    def __coerce__(self, other):
        if isinstance(other, int):
            return self, mpz(other)

# Here there be dragons
