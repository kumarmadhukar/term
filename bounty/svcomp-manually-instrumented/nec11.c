typedef enum myBool{ myFalse=0, myTrue=1 } myBool; // BOUNTY
extern myBool __VERIFIER_nondet_myBool();
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__noreturn__));
void reach_error() { __assert_fail("0", "nec11.c", 3, "reach_error"); }

void __VERIFIER_assert(int cond) {
  if (!(cond)) {
    ERROR: {reach_error();abort();}
  }
  return;
}

_Bool __VERIFIER_nondet_bool();

int main(){
   int a[5];
   int len=0;
   _Bool c=__VERIFIER_nondet_bool();
   int i;


   while(c){
     
      static myBool pStored0 = myFalse; // BOUNTY
      myBool flag = __VERIFIER_nondet_myBool(); // BOUNTY
      static int oldi, oldlen, olda[5], oldc; // BOUNTY
      if (pStored0) __CPROVER_assert(! (oldi == i && oldc == c && oldlen == len && __CPROVER_array_equal(olda, a)), "recurrent state found"); // BOUNTY
      if (flag) {  __CPROVER_array_copy(olda, a); oldi = i;  oldlen = len; oldc = c; pStored0 = myTrue; } // BOUNTY
      if (len==4)
         len =0;
      
      a[len]=0;

      len++;
   }
   __VERIFIER_assert(len==5);
   return 1;

   
}
