#!/usr/bin/env python3
#
#
#  WTINESS: CONVERTION OF CBMC TRACE INTO GRAPHML
#  Copyright (C) 2023-2042 TATA Consultancy Services Ltd. Ravindra Metta <r.metta@tcs.com>
#
#

import os,shutil,subprocess,re
import sys
import argparse,time
from datetime import datetime
from functools import partial

# This is the bug-fixed version on Oct-12-2024.

def extract_information(trace_file):
    output_data = []
    found_loop_head = False  # Flag to track the first occurrence of loop_head

    with open(trace_file, 'r') as file:
        for line in file:
            function_call_match = re.search(r'__VERIFIER_(reached_control|control_true|control_false|loop_head)\((\d+), "([^"]+)"', line)
            if function_call_match:
                control_type = function_call_match.group(1)
                line_number = function_call_match.group(2)
                function_name = function_call_match.group(3)

                # Map control type to new format
                if control_type == 'reached_control':
                    control_type = 'reachedControl'
                elif control_type == 'control_true':
                    control_type = 'trueBranch'
                elif control_type == 'control_false':
                    control_type = 'falseBranch'
                elif control_type == 'loop_head':
                    control_type = 'loopHead'
                else :
                    print("In the else case :",function_call_match)
                    # if not found_loop_head:
                    #     found_loop_head = True  # Set the flag after first loop_head

                #output_data.append(f"{function_name} {line_number} {control_type}")
                output_data.append("%s %s %s" % (function_name, line_number, control_type))
    return output_data
def process_data(extracted_data):
    index = 0
    last_loop_reachedControl_index=-1
    while index < len(extracted_data) - 1:
        current_line = extracted_data[index]
        next_line = extracted_data[index + 1]
        current_line_number = current_line.split(' ')[1]
        
        # Case 1: current line and next line contain 'loopHead', insert 'reachedControl' between them
        if 'loopHead' in current_line:
            if 'loopHead' in next_line:
                extracted_data.insert(index + 1, f'main {current_line_number} reachedControl')
                index+=1
        # Case 2: current line contains 'loopHead' and next line contains 'reachedControl' insert 'falseBranch after 'reachedControl'
            #if 'reachedControl' in next_line: #end of previous control statement
                #extracted_data.insert(index + 1, f'main {current_line_number} reachedControl')
                #extracted_data.insert(index + 2, f'main {current_line_number} falseBranch')
                #index+=2
        # Case 3: If current line and next line contain 'reachedControl', insert 'falseBranch' between them
        if 'reachedControl' in current_line : #hanging reachedControl handling
            #if 'reachedControl' in next_line:
                #extracted_data.insert(index + 1, f'main {current_line_number} falseBranch')
                #index+=1
            if 'loopHead' in next_line:
                last_loop_reachedControl_index=index
        index += 1
    if last_loop_reachedControl_index!=-1:
        extracted_data.insert(last_loop_reachedControl_index,'enteringLasso')
    return extracted_data

def write_output(output_data, output_file):
    with open(output_file, 'w') as file:
        for item in output_data:
            file.write(item + '\n')

def wit_gen(file_content):
    print("Traversing through the file:")
    for line in file_content:
        print(line)

def generateSHA1Sum():
    global NEW_C_FILE,TEST_SUITE_DIR,WITNESS
    #sha1runCmd = "sha1sum "+NEW_C_FILE
    # Changed as this file is also modified.
    #origCFile = os.environ["C_FILENAME"]
    origCFile = os.environ["CFILEFORSHA"]
    print("ORIG CFILE = " + origCFile)
    if(len(origCFile) == 0):
        origCFile = NEW_C_FILE
    sha1runCmd = "sha256sum "+ origCFile
    sha1output = subprocess.check_output(sha1runCmd,shell=True)
    print(sha1output)

    # Convert bytes to Unicode string (Python 3) or leave it as is (Python 2)
    if isinstance(sha1output, bytes):
        sha1output = sha1output.decode('utf-8')

    sha1value = re.findall('\w+',sha1output)[0]
    #print "SHA1 VALUE : " + sha1value
    dateOutput = subprocess.check_output("date \"+%FT%T%:z\"",shell=True)
    # Convert bytes to Unicode string (Python 3) or leave it as is (Python 2)
    if isinstance(dateOutput, bytes):
        dateOutput = dateOutput.decode('utf-8')

    os.environ['WITNESS_SRC'] = origCFile
    os.environ['WITNESS_SHA'] = sha1value
    os.environ['WITNESS_DOB'] = dateOutput.strip()


    WITNESS = os.environ['WITNESS_FILENAME']
    print("\n Witness file name is " + WITNESS)
    if (os.path.exists(WITNESS)):
        os.remove(WITNESS)
        print("\nDeleting previously generated witness file..\n")

def generateViolationWitness(tracefilelines):
    generateSHA1Sum()
    
    #study generated withness file along with code to debug
    if (len(tracefilelines)!=0):
        print("FINAL tracefilelines FIlE LINE ******************************\n")
        print('\n'.join(tracefilelines))
        witFileLines = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n"
        witFileLines += writeNonTermPrologue() #write Prologue
        witFileLines += "\t<graph edgedefault=\"directed\"> \n" #start graph 
        witFileLines += writeCodeInformation()

        # write nodes to graphml
        witFileLines += "\t\t<node id=\"N0\"> \n" + "\t\t\t<data key=\"entry\">true</data> \n" + "\t\t</node> \n"     # Entry Node
        edgeList = []
        nodeNumber = 1
        itr = 0 
        length = tracefilelines.__len__()
        prevLineNo = -1
        unroll = 0
        enteredLasso = False
        while(itr < length):
            if ("enteringLasso" in  tracefilelines[itr]):
                enteredLasso = True
                itr += 1
                continue
            lineWords = tracefilelines[itr].split()
            #print("LineWords:",lineWords)
            edgeType = ""
            nodeType = ""
            startLine = endLine = lineWords[1]
            if lineWords[-1].__contains__('reachedControl'):
                #print("linewords :",)
                startLine = endLine = lineWords[-2]
                # if "enteringLasso" in tracefilelines[itr+1].split():           #adding check for enterring lasso in between extracted data parsed lines
                #     nextLineWords = tracefilelines[itr+2].split()
                #     enteredLasso = True
                # else :
                nextLineWords = tracefilelines[itr+1].split()
                #print("next line words :",nextLineWords)  
                nextLineNo = nextLineWords[-2]
                nextNodeType = nextLineWords[-1]
                endLine = nextLineNo
                
                if nextNodeType.__contains__('falseBranch'):
                    edgeType += 'condition-false '
                else:
                    edgeType += 'condition-true '
                    if (enteredLasso):
                        print("Trace file line inside enterred lasso check :",tracefilelines[itr])
                        edgeType += 'cyclehead '
                        nodeType += 'cyclehead '
                        nontermloopNode = nodeNumber
                        nonTermLoopLineNo = startLine
                        enteredLasso = False
                itr += 1
            itr += 1
            
            #backedge
            startLine = str(max(int(startLine), int(prevLineNo)))
            
            witFileLines += writeNode(str(nodeNumber), nodeType)
            edgeList.append([edgeType, startLine, endLine])
            nodeNumber += 1
            prevLineNo = endLine

        backEdgeLineNo = prevLineNo
        # write Edges
        for i, node in enumerate(edgeList):
            edgeType = edgeList[i][0]
            startLine = edgeList[i][1]
            endLine = edgeList[i][2]
            witFileLines += writeEdge(i, edgeType, startLine, endLine)
        
        #write final edge from last node to cyclehead 
        i += 1
        lineNum = edgeList[-1][1]
        edgeType = edgeList[-1][0]
        witFileLines += "\t\t<edge id=\"E" + str(i) +  "\" source=\"N" + str(i) + "\" target=\"N" + str(nontermloopNode) +"\">\n" +\
            "\t\t\t<data key=\"startline\">" + backEdgeLineNo + "</data>\n" +\
            "\t\t\t<data key=\"endline\">" + str(nonTermLoopLineNo) + "</data>\n"
        witFileLines += "\t\t\t<data key=\"enterLoopHead\">true</data>\n"
        #witFileLines += "\t\t\t<data key=\"control\">condition-true</data>\n"
        witFileLines += "\t\t</edge>\n"

        # close graph
        witFileLines += "\t</graph>\n"
        witFileLines += "</graphml>"
        nonTermWit_file = open(os.environ['WITNESS_FILENAME'], 'w')
        nonTermWit_file.write(witFileLines)
        nonTermWit_file.close()
        print('\nWitness file generated successfully\n')
        return True
    else :
        print("\nWitness executable not created.. Problem may exist in witness file compilation.. Check logs..\n")
        return False

def writeNonTermPrologue():
    lines = ""
    lines += "<graphml xmlns=\"http://graphml.graphdrawing.org/xmlns\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"                  xsi:schemaLocation=\"http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd\">)" + '\n'
    lines += "\t<key id=\"programfile\" attr.name=\"programfile\" for=\"graph\"/>" + '\n'
    lines += "\t<key id=\"programhash\" attr.name=\"programhash\" for=\"graph\"/>" + '\n'
    lines += "\t<key id=\"sourcecodelang\" attr.name=\"sourcecodelang\" for=\"graph\"/>" + '\n'
    lines += "\t<key id=\"producer\" attr.name=\"producer\" for=\"graph\"/>" + '\n'
    lines += "\t<key id=\"specification\" attr.name=\"specification\" for=\"graph\"/>" + '\n'
    lines += "\t<key id=\"creationtime\" attr.name=\"creationtime\" for=\"graph\"/>" + '\n'
    lines += "\t<key id=\"witness-type\" attr.name=\"witness-type\" for=\"graph\"/>" + '\n'
    lines += "\t<key id=\"architecture\" attr.name=\"architecture\" for=\"graph\"/>" + '\n'
    lines += "\t<key id=\"memorymodel\" attr.name=\"memoryModel\"  attr.type = \"string\" for=\"graph\"/>" + '\n'
    lines += "\t<key attr.name=\"startline\"  attr.type = \"string\" for=\"edge\" id=\"startline\"/>" + '\n'
    lines += "\t<key attr.name=\"endline\"  attr.type = \"string\" for=\"edge\" id=\"endline\"/>" + '\n'
    lines += "\t<key attr.name=\"assumption\" attr.type=\"string\" for=\"edge\" id=\"assumption\"/>\n"
    lines += "\t<key attr.name=\"assumption.scope\" attr.type=\"string\" for=\"edge\" id=\"assumption.scope\"/>\n"
    lines += "\t<key attr.name=\"assumption.resultfunction\" attr.type=\"string\" for=\"edge\" id=\"assumption.resultfunction\"/>\n"
    lines += "\t<key id=\"entry\" attr.name=\"entry\" for=\"node\">\n" + "\t\t<default>false</default>\n" + "\t</key>\n"
    lines += "\t<key id=\"cyclehead\" attr.name=\"cyclehead\" for=\"node\">\n" + "\t\t<default>false</default>\n" + "\t</key>\n"
    lines += "\t<key id=\"enterLoopHead\" attr.name=\"enterLoopHead\" for=\"edge\">\n" + "\t\t<default>false</default>\n" + "\t</key>\n"
    lines += "\t<key id=\"control\" attr.name=\"control\" for=\"edge\"/>\n"
    lines += "\t<key id=\"originfile\" attr.name=\"originfile\" for=\"edge\"/>\n"
    lines += "\t<key id=\"sourcecode\" attr.name=\"sourcecode\" for=\"edge\"/>\n"
    return lines

def writeCodeInformation():
    lines = ""
    lines += "\t\t<data key=\"programfile\">" +  os.environ['WITNESS_SRC'] + "</data>\n" #insert code path
    lines += "\t\t<data key=\"programhash\">" +  os.environ['WITNESS_SHA'] + "</data>\n" #insert hash
    lines += "\t\t<data key=\"sourcecodelang\">C</data>\n"
    lines += "\t\t<data key=\"producer\">PROTON</data>\n"
    lines += "\t\t<data key=\"specification\">CHECK( init(main()), LTL(F end) ) </data>\n" #check
    utcTime = re.sub("\+.*", "", os.environ['WITNESS_DOB'])
    lines += "\t\t<data key=\"creationtime\">" + utcTime+"Z" + "</data>\n" #insert time
    lines += "\t\t<data key=\"witness-type\">violation_witness</data>\n"
    bit = os.environ["BIT"]
    lines += "\t\t<data key=\"architecture\">" + bit +"bit</data>\n"
    return lines

def writeNode(nodeId, nodeType):
    node = ""
    if nodeType.__contains__('cyclehead'):
        node += "\t\t<node id=\"N" + nodeId + "\">\n" + "\t\t\t<data key=\"cyclehead\">true</data>\n" + "\t\t</node>\n"
    else:
        node += "\t\t<node id=\"N" + nodeId + "\"/>\n"
    return node

def writeEdge(edgeNo, edgeType, startLine, endLine):
    i = edgeNo
    edge = ""    
    edge += "\t\t<edge id=\"E" + str(i) +  "\" source=\"N" + str(i) + "\" target=\"N" + str(i+1) +"\">\n" +\
            "\t\t\t<data key=\"startline\">" + startLine + "</data>\n" +\
            "\t\t\t<data key=\"endline\">" + endLine + "</data>\n"
    if edgeType.__contains__('cyclehead'):
        edge += "\t\t\t<data key=\"enterLoopHead\">true</data>\n"
        #edge += "\t\t\t<data key=\"control\">condition-true</data>\n"
    if edgeType.__contains__("condition"):
        edge += "\t\t\t<data key=\"control\">" + edgeType.split()[0] + "</data>\n"
    edge += "\t\t</edge>\n"
    return edge

if __name__ == "__main__":
    # Check if exactly four arguments have been provided
    if len(sys.argv) != 5:  # Remember, sys.argv[0] is the script name
        print("Usage: parse_trace_vf.py <trace-file> <src-file-for-SHA> <full-path-of-witness-file> <32|64>")
        sys.exit(1)  # Exit with a non-zero status to indicate an error

    trace_file = sys.argv[1]
    os.environ["CFILEFORSHA"] = sys.argv[2]
    os.environ['WITNESS_FILENAME'] = sys.argv[3]
    os.environ['BIT'] = sys.argv[4]
    output_file = 'tr_output.txt'

    extracted_data = extract_information(trace_file)
    #print("Printing extracted data :")
    #for item in extracted_data:
        #print(item)
    processed_data = process_data(extracted_data)
    #Print processed data
    # print("Processed Data is")
    # for item in processed_data:
    #     print(item)
        #2 pre-processing:1(api))remove unnecessary reached control(not followed by true or false branches),2(api))for each unnecessary reached control add a true branch
    generateViolationWitness(processed_data)

