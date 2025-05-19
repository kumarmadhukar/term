typedef enum myBool{ myFalse=0, myTrue=1 } myBool; // BOUNTY
extern myBool __VERIFIER_nondet_myBool();
/*
 * Date: 2014-06-01
 * Author: heizmann@informatik.uni-freiburg.de
 *
 */
extern int __VERIFIER_nondet_int(void);

int main() {
	int a[1048];

	a[2] = __VERIFIER_nondet_int();

        myBool pStored0 = myFalse; // BOUNTY
	while (a[2] >= 0) {
/* BOUNTY BEG */
            static int olda[1048];
  myBool flag = __VERIFIER_nondet_myBool();
  if (pStored0) { __CPROVER_assert(!(__CPROVER_array_equal(olda, a)), "recurrent state found"); }
  if (flag) {  __CPROVER_array_copy(olda, a); pStored0 = myTrue; }
/* BOUNTY END */
		a[2] = a[2] - 1;
		a[1+1] = __VERIFIER_nondet_int();
	}
	return 0;
}
