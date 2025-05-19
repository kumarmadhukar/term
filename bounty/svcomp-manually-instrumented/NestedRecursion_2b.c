typedef enum myBool{ myFalse=0, myTrue=1 } myBool; // BOUNTY
extern myBool __VERIFIER_nondet_myBool();
/*
 * Date: 07/07/2015
 * Created by: Ton Chanh Le (chanhle@comp.nus.edu.sg)
 * Adapted from "Inductive Invariants for Nested Recursion"
 * by Sava Krstic and John Matthews
 */

extern int __VERIFIER_nondet_int();

int g(int x)
{
  if (x == 0) 
    return 1;
  else {
      static myBool pStored0 = myFalse; // BOUNTY
      myBool flag = __VERIFIER_nondet_myBool(); // BOUNTY
      static int oldx; // BOUNTY
      if (pStored0) __CPROVER_assert(! (oldx == x), "recurrent state found"); // BOUNTY
      if (flag) { oldx = x; pStored0 = myTrue; } // BOUNTY
    return g(g(x - 1) + 1);
   }
}

int main() {
  int x = __VERIFIER_nondet_int();
  if (x < 0) return 0;
  g(x);
}
