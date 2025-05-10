#!/bin/bash
# tool

INFILE=$1
UW=$2

   echo UNWIND=$UW
   # TODO --- get the architecture from the command line
   #echo cbmc  --$BIT_WIDTH --unwind $UW -D __VERIFIER_assert=orignial__VERIFIER_assert -D __assert_fail=original__assert_fail  --no-built-in-assertions --stop-on-fail --object-bits 16 --string-abstraction $INFILE --trace --trace-show-function-calls --z3
   #cbmc  --$BIT_WIDTH --unwind $UW -D __VERIFIER_assert=orignial__VERIFIER_assert -D __assert_fail=original__assert_fail  --no-built-in-assertions --stop-on-fail --object-bits 16 --string-abstraction $INFILE --compact-trace --trace-show-function-calls --z3
   echo cbmc  --$BIT_WIDTH --unwind $UW -D __VERIFIER_assert=orignial__VERIFIER_assert -D __assert_fail=original__assert_fail  --no-built-in-assertions --stop-on-fail --object-bits 16 $INFILE --trace --trace-show-function-calls --z3
   cbmc  --$BIT_WIDTH --unwind $UW -D __VERIFIER_assert=orignial__VERIFIER_assert -D __assert_fail=original__assert_fail  --no-standard-checks  --no-built-in-assertions --stop-on-fail --object-bits 16 $INFILE --compact-trace --trace-show-function-calls --z3
   EV=$?
   if [ $EV -eq 10 ]
   then
       #grep "recurrent state found" $INFILE.err
       #pcregrep -M "^Violated property.*\n.*\n[ ]*recurrent state found[ \t]*\n" $INFILE.15TO.z3err
       #if [ $? -eq 0 ]
       #then
          echo $INFILE RECURRENT STATE FOUND AT UNWIND $UW >> $HOME/temp/x.txt
          exit $EV
       #fi
   fi
   
   # Exited due to Sig 6? Mostly due to Z3 internal error (map::at). No point in running at higher unwinds.
   if [ $EV -eq 6 ]
   then
          echo $INFILE RECURRENT STATE NOFOUND AT UNWIND $UW. Z3 internal error
          exit $EV
   fi

   
   # Exited due to sig 137 ? Mostly due to out of memory. No point in running at higher unwinds
   if [ $EV -eq 137 ]
   then
      echo $INFILE RECURRENT STATE NOFOUND AT UNWIND $UW. OUT OF MEMORY
      exit $EV
   fi

   echo $INFILE RECURRENT STATE NOTFOUND AT UNWIND $UW echo $EV

   exit $EV
