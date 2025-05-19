typedef enum myBool{ myFalse=0, myTrue=1 } myBool; // BOUNTY
extern myBool __VERIFIER_nondet_myBool();
extern void abort(void);
extern void __assert_fail(const char *, const char *, unsigned int, const char *) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__noreturn__));
void reach_error() { __assert_fail("0", "n.c11.c", 3, "reach_error"); }

void __VERIFIER_assert(int cond) {
  if (!(cond)) {
    ERROR: {reach_error();abort();}
  }
  return;
}

extern _Bool __VERIFIER_nondet_bool();

int main(){
   int a[5];
   unsigned int len=0;

   int i;
   int nondet; // BOUNTY


   while(nondet = __VERIFIER_nondet_bool()){
     
      static myBool pStored0 = myFalse; // BOUNTY
      myBool flag = __VERIFIER_nondet_myBool(); // BOUNTY
      static int oldi, oldlen, olda[5], oldnondet; // BOUNTY
      if (pStored0) __CPROVER_assert(! (oldi == i && oldnondet == nondet && oldlen == len && __CPROVER_array_equal(olda, a)), "recurrent state found"); // BOUNTY
      if (flag) {  __CPROVER_array_copy(olda, a); oldi = i;  oldlen = len; oldnondet = nondet; pStored0 = myTrue; } // BOUNTY
      if (len==4)
         len =0;
      
      a[len]=0;

      len++;
   }
   __VERIFIER_assert(len>=0 && len<5);
   return 1;

   
}

