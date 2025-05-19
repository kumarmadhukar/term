typedef enum myBool{ myFalse=0, myTrue=1 } myBool; // BOUNTY
extern myBool __VERIFIER_nondet_myBool();
/*
 * Date: 07/07/2015
 * Created by: Ton Chanh Le (chanhle@comp.nus.edu.sg)
 */

extern int __VERIFIER_nondet_int();

int binary_search(int i, int j)
{
  int nondet;
  if (i>=j) return i;
  int mid = (i+j)/2;
  if (nondet = __VERIFIER_nondet_int())
  { // BOUNTY
      static myBool pStored0 = myFalse; // BOUNTY
      myBool flag = __VERIFIER_nondet_myBool(); // BOUNTY
      static int oldi, oldj, oldmid, oldnondet; // BOUNTY
      if (pStored0) __CPROVER_assert(! (oldi == i && oldj == j && oldmid == mid && oldnondet == nondet), "recurrent state found");
      if (flag) { oldi = i; oldj = j; oldmid = mid; oldnondet = nondet; pStored0 = myTrue; } // BOUNTY
    return binary_search(i,mid);
  } // BOUNTY
  else {  // BOUNTY
      static myBool pStored1 = myFalse; // BOUNTY
      myBool flag = __VERIFIER_nondet_myBool(); // BOUNTY
      static int oldi, oldj, oldmid, oldnondet; // BOUNTY
      if (pStored1) __CPROVER_assert(! (oldi == i && oldj == j && oldmid == mid && oldnondet == nondet), "recurrent state found");
      if (flag) { oldi = i; oldj = j; oldmid = mid; oldnondet = nondet; pStored1 = myTrue; } // BOUNTY
  }
  return binary_search(mid+1,j);
}


int main() {
  int x = __VERIFIER_nondet_int();
  int y = __VERIFIER_nondet_int();
  //prevent overflows
  if(!(-1073741823<=x && x<=1073741823)) return 0;
  if(!(-1073741823<=y && y<=1073741823)) return 0;
  binary_search(x, y);
}
