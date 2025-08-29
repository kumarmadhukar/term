#!/bin/bash

#
# PROTON
# (C) 2022-2042, Kumar Madhukar
# Department of Computer Science and Engineering, Indian Institute of Technology Delhi
#


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
max_time=210

# Initialize the timer
start_time=$(date +%s)

# Function to check the elapsed time
elapsed_time() {
  current_time=$(date +%s)
  echo $((current_time - start_time))
}

run_gl_dummy() {
    return 137
}

run_gl() {
    echo "RUNNING GL for unwind $2"
    (timeout "$3" run-gl-uw.sh $1 "$2") >& $1.err
    gl_status=$?
    if [ $gl_status -eq 10 ]
    then
        RESTXT="FALSE(termination)"
        exit $gl_status
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
        exit $ki_status
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
      exit $z3_status
    fi

    if [ $z3_status -eq 6 ] || [ $z3_status -eq 137 ]; then
        echo "Z3 error or OUT OF MEM on unwind $num."
        exit $z3_status # Resource error
    fi

    return $z3_status
}

# Iterate through the unwind numbers
for num in "${numbers[@]}"; do
  # Calculate remaining allowed time
  remaining_time=$((max_time - $(elapsed_time)))

  # If no remaining time, break the loop
  if [ $remaining_time -le 0 ]; then
    run_z3 $1 "$num"
    exit_status=$?
    continue
  fi

  # Run glucose with the remaining time as timeout
  # Capture the exit status of glucose
  run_gl_dummy $1 "$num" "$remaining_time"
  exit_status=$?
  
  if [ $exit_status -eq 6 ] || [ $exit_status -eq 137 ]; then
     echo "GLUCOSE error or OUT OF MEM on unwind $num. exit_status=$exit_status"
     max_time=0 # Resource error. Move to Z3
     run_z3 $1 "$num"
     exit_status=$?
     continue
  fi

  # exit status 124 means timeout
  if [ $exit_status -eq 124 ]; then
     echo "GLUCOSE timed out on unwind $num."
     max_time=0 # Resource error. Move to Z3
     run_z3 $1 "$num"
     exit_status=$?
     continue
  fi

done

echo "run-one-bounty.sh completed successfully within the time limit."
exit 1  # Successful completion. But NT not found up to the unwind
