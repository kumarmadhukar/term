#!/bin/bash
# tool

#
# PROTON
# (C) 2022-2042, Kumar Madhukar
# Department of Computer Science and Engineering, Indian Institute of Technology Delhi
#



# Defn: RSA = Recurrent State Assertion
#
# Algo:
#      If  RSA not instrumented, skip the file for NT check
#
######  NT CHECK
#      Run cbmc-glucose for 2 min
#      If cbmc-glucose ran out of time,
#         run cbmc --z3 for 2 mins 
#      If NT found, geneate witness, but don't pass it on to validator yet
#
######  T CHECK
#      Run cbmc --z3 bounded termination for 2 min check fixing the range to 4 bit number (-8 to 7 for signed, and 0 to 7 for unsigned)
#
######  POLL 
#      Take a poll of NT and T checks
#      If NT, declare NT and pass the witness
#      else if T, declare T
#      else declare UNKNOWN
# END

# Initialize the exit codes
GLRV=0
Z3RV=0
TRES=0
NTRES=0
EXCO=0
RESTXT="DEFAULT"

echo  "
* *                 CBMC 5.95.0 (n/a) 64-bit                * *
* *                 Copyright (C) 2001-2018                 * *
* *              Daniel Kroening, Edmund Clarke             * *
* * Carnegie Mellon University, Computer Science Department * *
* *                  kroening@kroening.com                  * *
* *        Protected in part by U.S. patent 7,225,417       * *
* *  *****************************************************  * *
* *                 Built with Llama                        * *
* *  *****************************************************  * *
"
# If RSA present, then check for NT
grep -ql "recurrent state" $1
if [ $? -eq 0 ]
then
   # Try NT with GL
   #(/usr/bin/time -f "\t%E TIME \t%M MEMORY" timeout 2m run-one-gl.sh $1) >& $1.err
   #(timeout 2m run-one-gl.sh $1) >& $1.err
   #GLRV=$?  # Return value of above command
   
   ########   GLUCOSE is running out of memory, making the script exit. Make do with z3 for now.

   # If GL timeouts, try Z3
   #if [ $GLRV -eq 124 ]
   #then
      #(/usr/bin/time -f "\t%E TIME \t%M MEMORY" timeout 2m run-one-z3.sh $1) >& $1.err
      #(timeout 2m run-one-z3.sh $1) >& $1.err

      (timeout 3m run-one-bounty.sh $1) >& $1.err

      Z3RV=$?  # Return value of above command
   #fi

   if [ $GLRV -eq 10 ] || [ $Z3RV -eq 10 ] # Recurent State Assertion Failed. So, NT Found
   then
      NTRES=1
      TRES=10
      $TOOL_DIR/parse_trace_vf.py $1.err $2 $TOOL_DIR/$WITNESS_FILE $BIT_WIDTH
      #$TOOL_DIR/orig_parse_trace_vf.py $1.err $2 $TOOL_DIR/$WITNESS_FILE $BIT_WIDTH
   fi

   echo NT-CHECKRESULT. GLRV=$GLRV. Z3RV=$Z3RV. NTRES=$NTRES
else
   echo MISSING RSA
fi # end of NT check


# We do term chek only with Z3, in the best interest of time.
# If found NT, don't try t-check
if [ $NTRES -ne 1 ]
then
    (timeout 2m t-check.sh $2) >& $2.terr
    TRES=$?

    # If CBMC t-check is unsuccessful, try the Llama check
    if [ $TRES -ne 0 ]
    then

       if ! command -v llm-t-check.sh
       then
           echo "llm-t-check not found"
       fi
        
       # Check execute permission
       if [ -x "$TOOL_DIR/llm-t-check.sh" ]; then
           echo "llm-t-check has execute permission"
       else
           echo "llm-t-check does not have execute permission"
       fi
       
       ($TOOL_DIR/llm-t-check.sh $2) >& $2.terr
       TRES=$?
       echo "LLM_T_CHECK EXIT VAL $TRES"
    fi

    echo T-CHECKRESULT. TRES=$TRES
    EXCO=0
    RESTXT="DEFAULT"
fi

# By this point in this script:-
#  ---  NTRES is 1 if non-termination is found, 0 otherwise
#  ---  TRES is 10 if unwind assertions failes, 0 if termination found, else some other value
echo NTRES=$NTRES TRES=$TRES for $2
if [ $TRES -eq 0 ] && [ $NTRES -eq 1 ]
then
   RESTXT="UNKNOWN"
   EXCO=2 # 2 --> UNKNOWN
else if [ $NTRES -eq 1 ] && [ $TRES -eq 10 ]
then
   RESTXT="FALSE(termination)"
   EXCO=1 # 1 --> NT
else if [ $TRES -eq 0 ]
then
   RESTXT="TRUE"
   EXCO=0 # 0 --> T
else if [ $Z3RV -eq 6 ]
then
EXCO=4
RESTXT="SOLVER INTERNAL ERROR"
else
   RESTXT="$RESTXT INCONCLUSIVE"
   EXCO=3 # 0 --> T
fi
fi
fi
fi

echo FILE=$1 GLRES=$GLRV Z3RES=$Z3RV NTRES=$NTRES  TRES=$TRES TNT-RESULT=$RESTXT EXITCODE=$EXCO
exit $EXCO
