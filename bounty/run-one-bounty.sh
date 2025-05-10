#!/bin/bash

GLRV=0
Z3RV=0
TRES=0
NTRES=0
EXCO=0
RESTXT="DEFAULT"

echo  "
* *                 CBMC 6.5.0 (n/a) 64-bit                * *
* *                 Copyright (C) 2001-2018                 * *
* *              Daniel Kroening, Edmund Clarke             * *
* * Carnegie Mellon University, Computer Science Department * *
* *                  kroening@kroening.com                  * *
* *        Protected in part by U.S. patent 7,225,417       * *
"

grep -ql "recurrent state" $1
if [ $? -ne 0 ]
then
echo RSA ABSENT
exit 2
fi
# Define the list of numbers to iterate through
numbers=(2 3 4 10 12 20 40 100 1000)

# Total allowed time for glucose in seconds
max_time=225
LOC=`wc -l $2 | cut -d " " -f 1`
# for bigger files, do not run SAT solver; directly start with SMT solver
if [ $LOC -gt 3000 ];
then
   #max_time=225
   max_time=0
else
   max_time=225
fi

# Initialize the timer
start_time=$(date +%s)

# Function to check the elapsed time
elapsed_time() {
  current_time=$(date +%s)
  echo $((current_time - start_time))
}


run_gl() {
    echo "RUNNING GL for unwind $2"
    (timeout "$3" run-gl-uw.sh $1 "$2") >& $1.err
    gl_status=$?
    if [ $gl_status -eq 10 ]
    then
        RESTXT="FALSE(termination)"
        exit 1 # 1 --> NT
    fi

    return $gl_status
}

run_ki() {
    echo "RUNNING KISSAT for unwind $2"
    (timeout "$3" run-kissat-uw.sh $1 "$2") >& $1.err
    ki_status=$?
    if [ $ki_status -eq 10 ]
    then
        RESTXT="FALSE(termination)"
        exit 1
    fi

    return $ki_status
}


run_z3 () {
    echo "RUNNING Z3 for unwind $2"
    (run-z3-uw.sh $1 "$2") >& $1.err
    z3_status=$?

    if [ $z3_status -eq 10 ]
    then
      RESTXT="FALSE(termination)"
      exit 1 # 1 --> NT
    fi

    if [ $z3_status -eq 6 ] || [ $z3_status -eq 137 ]; then
        echo "Z3 EXITCODE=$z3_status on unwind $num."
        exit $z3_status # Resource error
    fi

    return $z3_status
}


# Iterate through the numbers
for num in "${numbers[@]}"; do
  # Calculate remaining allowed time for x1.sh
  remaining_time=$((max_time - $(elapsed_time)))

  # If no remaining time, break the loop
  if [ $remaining_time -le 0 ]; then
    run_z3 $1 "$num"
    exit_status=$?
    continue
  fi

  # Run x1.sh with the remaining time as timeout
  # Capture the exit status of x1.sh
  run_gl $1 "$num" "$remaining_time"
  exit_status=$?
  
  if [ $exit_status -eq 6 ] || [ $exit_status -eq 137 ]; then
    echo "GLUCOSE error or OUT OF MEM on unwind $num. exit_status=$exit_status"
     max_time=0 # Resource error. Move to Z3
    run_z3 $1 "$num"
    exit_status=$?
     continue
  fi

  # If x1.sh was terminated by the timeout, it returns 124
  if [ $exit_status -eq 124 ]; then
    echo "GLUCOSE timed out on unwind $num."
    max_time=0 # Resource error. Move to Z3
    run_z3 $1 "$num"
    exit_status=$?
    continue
  fi

done

echo "run-one-bounty.sh completed successfully within the time limit."
exit 2

