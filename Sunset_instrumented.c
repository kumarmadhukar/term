typedef enum {myFalse, myTrue} myBool; myBool __VERIFIER_nondet_myBool(void);
extern void __VERIFIER_reached_control(int, char const *);
extern void __VERIFIER_loop_head(int, char const *);
extern void __VERIFIER_control_true(int, char const *);
extern void __VERIFIER_control_false(int, char const *);
typedef enum {false,true} bool;

extern int __VERIFIER_nondet_int(void);

int main() {
    int i;
    i = __VERIFIER_nondet_int();
    
    while (i > 10) {printf("CBMC Instrumentation @ line9");static myBool pStored = myFalse;myBool flag=__VERIFIER_nondet_myBool();static int oi;if(pStored){__CPROVER_assert(!(oi==i),"recurrent state found");} if(flag){oi=i;pStored=myTrue;} __VERIFIER_loop_head(9, " ");

        if (i == 25) {
            i = 30;
        }
        if (i <= 30) {
            i = i-1;
        } else {
            i = 20;
        }
    }
    
    return 0;
}