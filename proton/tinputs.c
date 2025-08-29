//
// PROTON
// (C) 2022-2042, Kumar Madhukar
// Department of Computer Science and Engineering, Indian Institute of Technology Delhi
//



// TO CONSTRAIN THE VALUES OF INPUTS
#define __RANGE1
#define __BOUND_INP

#ifdef __RANGE1
#define UL 0  // unsigned lower bound
#define UU 7  // unsigned upper bound
#define SL -8 // signed lower bound
#define SU 7  // signed upper bound
#else
#ifdef __RANGE2
#define UL 0   // unsigned lower bound
#define UU 15  // unsigned upper bound
#define SL -16 // signed lower bound
#define SU 15  // signed upper bound
#else
#define UL 0   // unsigned lower bound
#define UU 31  // unsigned upper bound
#define SL -32 // signed lower bound
#define SU 31  // signed upper bound
#endif
#endif

#ifdef __BOUND_INP
#define __CONSTRAIN_RANGE(i, lb, ub) (__CPROVER_assume(((i) >=  lb) && ((i) <= ub)))
#else
#define __CONSTRAIN_RANGE(i, lb, ub) 
#endif

#define CONSTRAIN_NONDET(typestr, LB, UB) {\
   typestr currInp;\
   __CONSTRAIN_RANGE(currInp, LB, UB);\
   __CPROVER_input("__CONCRETE__"#typestr , currInp);\
   return currInp;\
}

#define CONSTRUCT_NONDET(typestr) {\
   typestr currInp;\
   __CPROVER_input("__CONCRETE__"#typestr , currInp);\
   return currInp;\
}

// Standard types needed for inputs. Add more types and APIs as needed.
typedef signed char int8_t;
typedef unsigned char uint8_t, uchar, unsigned_char;
typedef short int16_t;
typedef unsigned short uint16_t, ushort, unsigned_short;
typedef int int32_t;
typedef unsigned int uint32_t, uint, unsigned_int;

// As long long is 8 bytes on both 32 and 64 bit, used it for int64 and loff
typedef long long int int64_t;
typedef unsigned long long int uint64_t;
typedef long long int loff_t;

// As long is 8 bytes on 64 bit and 4 bytes on 32 bit, use it for size_t
typedef unsigned long int size_t, ulong, unsigned_long;

typedef uint8_t  u8;
typedef uint16_t u16;
typedef uint32_t u32;

typedef int8_t   s8;
typedef int16_t  s16;
typedef int32_t  s32;
typedef int64_t  s64;
typedef uint64_t u64;

typedef unsigned __int128 uint128;
typedef signed __int128 int128;

typedef void * voidptr;
typedef char * pchar;

typedef unsigned long sector_t;


// char nondet implementation
char __VERIFIER_nondet_char(void) CONSTRUCT_NONDET(char)
s8   __VERIFIER_nondet_S8(void)   CONSTRUCT_NONDET(s8)
s8   __VERIFIER_nondet_s8(void)   CONSTRUCT_NONDET(s8)

uchar         __VERIFIER_nondet_uchar(void)         CONSTRUCT_NONDET(uchar)
unsigned char __VERIFIER_nondet_unsigned_char(void) CONSTRUCT_NONDET(unsigned_char)
u8            __VERIFIER_nondet_U8(void)            CONSTRUCT_NONDET(u8)
u8            __VERIFIER_nondet_u8(void)            CONSTRUCT_NONDET(u8)


// short nondet implementation --- range constrained
short __VERIFIER_nondet_short(void) CONSTRAIN_NONDET(short, SL, SU)
s16   __VERIFIER_nondet_s16(void)   CONSTRAIN_NONDET(s16, SL, SU)

ushort         __VERIFIER_nondet_ushort(void)         CONSTRAIN_NONDET(ushort, UL, UU)
unsigned short __VERIFIER_nondet_unsigned_short(void) CONSTRAIN_NONDET(unsigned_short, UL, UU)
u16            __VERIFIER_nondet_u16(void)            CONSTRAIN_NONDET(u16, UL, UU)


// int nondet implementation --- range constrained
int __VERIFIER_nondet_int(void) CONSTRAIN_NONDET(int, SL, SU)
s32 __VERIFIER_nondet_S32(void) CONSTRAIN_NONDET(s32, SL, SU)
s32 __VERIFIER_nondet_s32(void) CONSTRAIN_NONDET(s32, SL, SU)

size_t __VERIFIER_nondet_size_t() CONSTRAIN_NONDET(size_t, UL, UU)

uint         __VERIFIER_nondet_uint(void)         CONSTRAIN_NONDET(uint, UL, UU)
u32          __VERIFIER_nondet_U32(void)          CONSTRAIN_NONDET(u32, UL, UU)
u32          __VERIFIER_nondet_u32(void)          CONSTRAIN_NONDET(u32, UL, UU)
unsigned_int __VERIFIER_nondet_unsigned(void)     CONSTRAIN_NONDET(unsigned_int, UL, UU)
unsigned_int __VERIFIER_nondet_unsigned_int(void) CONSTRAIN_NONDET(unsigned_int, UL, UU)


// long nondet implementation --- range constrained
long          __VERIFIER_nondet_long(void)          CONSTRAIN_NONDET(long, SL, SU)
unsigned long __VERIFIER_nondet_ulong(void)         CONSTRAIN_NONDET(ulong, UL, UU)
unsigned long __VERIFIER_nondet_unsigned_long(void) CONSTRAIN_NONDET(unsigned_long, UL, UU)


// long long nondet implementation --- range constrained
long long __VERIFIER_nondet_longlong(void) CONSTRAIN_NONDET(int64_t, SL, SU)
__int128  __VERIFIER_nondet_int128(void)   CONSTRAIN_NONDET(int128, SL, SU)

unsigned long long __VERIFIER_nondet_ulonglong(void) CONSTRAIN_NONDET(uint64_t, UL, UU)
unsigned __int128  __VERIFIER_nondet_uint128(void)   CONSTRAIN_NONDET(uint128, UL, UU)


// Unconstrained implementations
double __VERIFIER_nondet_double(void) CONSTRUCT_NONDET(double)
float __VERIFIER_nondet_float(void)   CONSTRUCT_NONDET(float)

_Bool __VERIFIER_nondet_bool(void)  CONSTRUCT_NONDET(_Bool)
_Bool __VERIFIER_nondet__Bool(void) CONSTRUCT_NONDET(_Bool)
_Bool __VERIFIER_nondet_Bool(void)  CONSTRUCT_NONDET(_Bool)

void * __VERIFIER_nondet_pointer(void)    CONSTRUCT_NONDET(voidptr)
char * __VERIFIER_nondet_pchar(void)      CONSTRUCT_NONDET(pchar)
loff_t __VERIFIER_nondet_loff_t(void)     CONSTRUCT_NONDET(loff_t)
sector_t __VERIFIER_nondet_sector_t(void) CONSTRUCT_NONDET(sector_t)

