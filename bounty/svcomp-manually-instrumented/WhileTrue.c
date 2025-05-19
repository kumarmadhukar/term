typedef enum myBool{ myFalse=0, myTrue=1 } myBool; // BOUNTY
extern myBool __VERIFIER_nondet_myBool();
/*
 * Date: 2013-12-16
 * Author: leike@informatik.uni-freiburg.de
 *
 * Very simple example for non-termination
 */
typedef enum {false, true} bool;

extern int __VERIFIER_nondet_int(void);

int main()
{
        myBool pStored0 = myFalse; // BOUNTY
	while (true) {
		// do nothing
        myBool flag = __VERIFIER_nondet_myBool();
        if (pStored0) { __CPROVER_assert(!(1), "recurrent state found"); }
        if (flag) {  pStored0 = myTrue; }
	}
	return 0;
}
