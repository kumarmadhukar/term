#!/bin/bash
# tool

#
# PROTON
# (C) 2022-2042, Kumar Madhukar
# Department of Computer Science and Engineering, Indian Institute of Technology Delhi
#


INFILE=$1
UW=$2

   echo UNWIND=$UW
   echo cbmc --external-sat-solver kissat --$BIT_WIDTH --unwind $UW -D __VERIFIER_assert=orignial__VERIFIER_assert -D __assert_fail=original__assert_fail  --no-built-in-assertions --stop-on-fail --object-bits 16 $INFILE --trace --trace-show-function-calls
   cbmc --external-sat-solver kissat  --$BIT_WIDTH --unwind $UW -D __VERIFIER_assert=orignial__VERIFIER_assert -D __assert_fail=original__assert_fail  --no-built-in-assertions --stop-on-fail --object-bits 16 $INFILE --compact-trace --trace-show-function-calls
   EV=$?
   echo EXIT STATUS is $EV
   if [ $EV -eq 10 ]
   then
       # grep "recurrent state found" $INFILE.err
       # pcregrep -M "recurrent state found\n" $INFILE.15TO.err
       #if [ $? -eq 0 ]
       #then
          echo $INFILE RECURRENT STATE FOUND AT UNWIND $UW >> $HOME/temp/x.txt
          exit $EV
       #fi
   fi

   # Exited due to sig 137 ? Mostly due to out of memory. No point in running at higher unwinds
   if [ $EV -eq 137 ]
   then
      echo $INFILE RECURRENT STATE NOFOUND AT UNWIND $UW. OUT OF MEMORY
      exit $EV
   fi

   echo $INFILE RECURRENT STATE NOTFOUND AT UNWIND $UW echo $EV
exit $EV
