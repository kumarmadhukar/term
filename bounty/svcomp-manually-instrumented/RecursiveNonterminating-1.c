typedef enum myBool{ myFalse=0, myTrue=1 } myBool; // BOUNTY
extern myBool __VERIFIER_nondet_myBool();
/*
 * Author: Matthias Heizmann
 * Date: 2014-06-29
 * 
 */

extern int __VERIFIER_nondet_int(void);


void rec(int x, int y) {
	if (x <= 23 && x >= -42) {
/* BOUNTY BEG */
        static myBool pStored0 = myFalse; // BOUNTY
        static unsigned int oldx, oldy;
        myBool flag = __VERIFIER_nondet_myBool();
        if (pStored0) { __CPROVER_assert(!(oldx == x  && oldy == y), "recurrent state found"); }
        if (flag) {  oldx = x; oldy = y; pStored0 = myTrue; }
/* BOUNTY END */
		rec(2*y-2, x + 1);
	}
}

int main() {
    int n = __VERIFIER_nondet_int();
    if(!(n<=2147483646)) return 0;
    rec(n, n + 1);
    return 0;
}
