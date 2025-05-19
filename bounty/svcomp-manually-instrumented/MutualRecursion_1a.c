typedef enum myBool{ myFalse=0, myTrue=1 } myBool; // BOUNTY
extern myBool __VERIFIER_nondet_myBool();
/*
 * Date: 07/07/2015
 * Created by: Ton Chanh Le (chanhle@comp.nus.edu.sg)
 */

extern int __VERIFIER_nondet_int();

int f(int x);
int g(int x);

int f(int x) 
{ 
  if (x <= 0) return 0; 
  else
  { // BOUNTY
      static myBool pStored1 = myFalse; // BOUNTY
      myBool flag = __VERIFIER_nondet_myBool(); // BOUNTY
      static int oldx; // BOUNTY
      if (pStored1) __CPROVER_assert(! (oldx == x), "recurrent state found");
      if (flag) { oldx = x; pStored1 = myTrue; } // BOUNTY
      return g(x) + g(x + 1); 
  }
}

int g(int x) 
{ 
  if (x <= 0) return 0; 
  else
  { // BOUNTY
      static myBool pStored0 = myFalse; // BOUNTY
      myBool flag = __VERIFIER_nondet_myBool(); // BOUNTY
      static int oldx; // BOUNTY
      if (pStored0) __CPROVER_assert(! (oldx == x), "recurrent state found");
      if (flag) { oldx = x; pStored0 = myTrue; } // BOUNTY
      return f(x - 1) + f(x - 2); 
  }
}


int main() {
  int x = __VERIFIER_nondet_int();
  g(x);
}
