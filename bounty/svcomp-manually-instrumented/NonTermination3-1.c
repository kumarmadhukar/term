typedef enum myBool{ myFalse=0, myTrue=1 } myBool; // BOUNTY
extern myBool __VERIFIER_nondet_myBool();
/*
 * Date: 2014-06-26
 * Author: leike@informatik.uni-freiburg.de
 *
 */

extern int __VERIFIER_nondet_int();

int main() {
	int i = __VERIFIER_nondet_int();
	int a[10];

	for (int n = 0; n < 10; ++n) {
		a[n] = __VERIFIER_nondet_int();
	}

        myBool pStored0 = myFalse; // BOUNTY
	while (0 <= i && i < 10 && a[i] >= 0) {
/* BOUNTY BEG */
            static int olda[10], oldi;
  myBool flag = __VERIFIER_nondet_myBool();
  if (pStored0) { __CPROVER_assert(!(__CPROVER_array_equal(olda, a) && oldi == i), "recurrent state found"); }
  if (flag) {  __CPROVER_array_copy(olda, a); oldi = i; pStored0 = myTrue; }
/* BOUNTY END */
		i = __VERIFIER_nondet_int();
		/* possible invalid dereference */
		a[i] = 0;
	}
	return 0;
}
