typedef enum myBool{ myFalse=0, myTrue=1 } myBool; // BOUNTY
extern myBool __VERIFIER_nondet_myBool();
/*
 * Date: 06/07/2015
 * Created by: Ton Chanh Le (chanhle@comp.nus.edu.sg)
 * Adapted from AProVE_numeric/ex3.c
 */

extern int __VERIFIER_nondet_int();
int rec1(int i);
int rec2(int j);

int rec1(int i) {
  if(i <= 0)
    return 0;
  return rec1(rec1(rec1(i-2) - 1)) + 1;
}

int rec2(int j) {
  if(j <= 0)
    return 0;
      static myBool pStored0 = myFalse; // BOUNTY
      myBool flag = __VERIFIER_nondet_myBool(); // BOUNTY
      static int oldj; // BOUNTY
      if (pStored0) __CPROVER_assert(! (oldj == j), "recurrent state found"); // BOUNTY
      if (flag) { oldj = j; pStored0 = myTrue; } // BOUNTY
  return rec2(rec1(j+1)) - 1;
}

int main() {
  int x = __VERIFIER_nondet_int();
  //prevent overflows
  if(!(x<=2147483646)) return 0;
  rec2(x);
}
