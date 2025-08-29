"""
PROTON
(C) 2022-2042, Kumar Madhukar
Department of Computer Science and Engineering, Indian Institute of Technology Delhi
"""

import re
import sys

def extract_information(trace_file):
    output_data = []

    with open(trace_file, 'r') as file:
        for line in file:
            # Extract variable assignments
            assignment_match = re.search(r'\s+(\w+)=(\d+) \(', line)
            if assignment_match:
                variable = assignment_match.group(1)
                value = assignment_match.group(2)
                output_data.append(f"{variable}={value}")
                #print matched data
                #print(f"{variable}={value}")
            # Extract __VERIFIER_* function calls
            function_call_match = re.search(r'__VERIFIER_(reached_control|control_true|control_false|loop_head)\((\d+), "([^"]+)",', line)
            if function_call_match:
                output_data.append(f"{function_call_match.group(1)}({function_call_match.group(2)}, {function_call_match.group(3)})")
                #print matched data
                #print(f"{function_call_match.group(1)}({function_call_match.group(2)}, {function_call_match.group(3)})")

    return output_data

def write_output(output_data, output_file):
    with open(output_file, 'w') as file:
        for item in output_data:
            file.write(item + '\n')

if __name__ == "__main__":
    trace_file = sys.argv[1]
    output_file = 'tr_output.txt'

    extracted_data = extract_information(trace_file)
    #print extracted data
    # for item in extracted_data:
    #     print(item)

    write_output(extracted_data, output_file)
