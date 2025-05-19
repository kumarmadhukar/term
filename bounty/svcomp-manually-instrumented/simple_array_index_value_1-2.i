typedef enum myBool{ myFalse=0, myTrue=1 } myBool; // BOUNTY
extern myBool __VERIFIER_nondet_myBool();





extern void abort(void);

extern void __assert_fail (const char *__assertion, const char *__file,
      unsigned int __line, const char *__function)
     __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__noreturn__));
extern void __assert_perror_fail (int __errnum, const char *__file,
      unsigned int __line, const char *__function)
     __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__noreturn__));
extern void __assert (const char *__assertion, const char *__file, int __line)
     __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__noreturn__));

void reach_error() { ((void) sizeof ((0) ? 1 : 0), __extension__ ({ if (0) ; else __assert_fail ("0", "simple_array_index_value_1-2.c", 7, __extension__ __PRETTY_FUNCTION__); })); }
extern void abort(void);
void assume_abort_if_not(int cond) {
  if(!cond) {abort();}
}
void __VERIFIER_assert(int cond)
{
  if (!(cond)) {
    ERROR: {reach_error();abort();}
  }
  return;
}

unsigned int __VERIFIER_nondet_uint();

int main()
{
  unsigned int array[10000];
  unsigned int index = 0;
  unsigned int tmp = 0;

    myBool pStored0 = myFalse;
  while (1) {
      myBool flag = __VERIFIER_nondet_myBool(); // BOUNTY
      static unsigned int oldarray[10000],  oldindex, oldtmp; // BOUNTY
      if (pStored0) __CPROVER_assert(! (__CPROVER_array_equal(oldarray, array)  && oldindex == index && oldtmp == tmp), "recurrent state found"); // BOUNTY
      if (flag) {  __CPROVER_array_copy(oldarray, array); oldindex = index;  oldtmp = tmp; pStored0 = myTrue; } // BOUNTY
    index = __VERIFIER_nondet_uint();
    if (index >= 10000) {
      break;
    }
    array[index] = index;
    tmp = index;
  }

  __VERIFIER_assert(tmp < 10000 && array[tmp] == tmp);


}
