
"""
PROTON
(C) 2022-2042, Kumar Madhukar
Department of Computer Science and Engineering, Indian Institute of Technology Delhi
"""

import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom


def parse_trace_file(trace_file_path):
    parsed_data = {
        "loop_head": [],
        "reached_control": [],
        "control_true": [],
        "control_false": []
    }

    parsed_data_list = []

    with open(trace_file_path, 'r') as file:
        for line in file:
            if "loop_head" in line:
                # Extract line number and function name
                parts = line.split("(")[1].split(")")[0].split(", ")
                parsed_data["loop_head"].append((int(parts[0]), parts[1].strip()))
                #Append tuple (loop_head, line number, function name) to parsed_data_list
                parsed_data_list.append(("loop_head", int(parts[0]), parts[1].strip()))
            elif "reached_control" in line:
                parts = line.split("(")[1].split(")")[0].split(", ")
                parsed_data["reached_control"].append((int(parts[0]), parts[1].strip()))
                #Append tuple (reached_control, line number, function name) to parsed_data_list
                parsed_data_list.append(("reached_control", int(parts[0]), parts[1].strip()))
            elif "control_true" in line:
                parts = line.split("(")[1].split(")")[0].split(", ")
                parsed_data["control_true"].append((int(parts[0]), parts[1].strip()))
                #Append tuple (control_true, line number, function name) to parsed_data_list
                parsed_data_list.append(("control_true", int(parts[0]), parts[1].strip()))
            elif "control_false" in line:
                parts = line.split("(")[1].split(")")[0].split(", ")
                parsed_data["control_false"].append((int(parts[0]), parts[1].strip()))
                #Append tuple (control_false, line number, function name) to parsed_data_list
                parsed_data_list.append(("control_false", int(parts[0]), parts[1].strip()))

    return parsed_data, parsed_data_list


def create_graphml_structure(parsed_trace_data, parsed_trace_data_list):
    graphml = ET.Element("graphml")
    graph = ET.SubElement(graphml, "graph", edgedefault="directed")

    graphml = ET.Element("graphml", {
        "xmlns": "http://graphml.graphdrawing.org/xmlns",
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:schemaLocation": "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
    })

    # Define keys for the GraphML header
    keys_info = [
    {"id": "programfile", "attr.name": "programfile", "for": "graph"},
    {"id": "programhash", "attr.name": "programhash", "for": "graph"},
    {"id": "sourcecodelang", "attr.name": "sourcecodelang", "for": "graph"},
    {"id": "producer", "attr.name": "producer", "for": "graph"},
    {"id": "specification", "attr.name": "specification", "for": "graph"},
    {"id": "creationtime", "attr.name": "creationtime", "for": "graph"},
    {"id": "witness-type", "attr.name": "witness-type", "for": "graph"},
    {"id": "architecture", "attr.name": "architecture", "for": "graph"},
    {"id": "entry", "attr.name": "entry", "for": "node", "default": "false"},
    {"id": "nodetype", "attr.name": "nodetype", "for": "node", "default": "path"},
    {"id": "violation", "attr.name": "violation", "for": "node", "default": "false"},
    {"id": "cyclehead", "attr.name": "cyclehead", "for": "node", "default": "false"},
    {"id": "invariant", "attr.name": "invariant", "for": "node", "default": "true"},
    {"id": "threadId", "attr.name": "threadId", "for": "edge"},
    {"id": "endline", "attr.name": "endline", "for": "edge"},
    {"id": "enterLoopHead", "attr.name": "enterLoopHead", "for": "edge", "default": "false"},
    {"id": "createThread", "attr.name": "createThread", "for": "edge"},
    {"id": "enterFunction", "attr.name": "enterFunction", "for": "edge"},
    {"id": "startline", "attr.name": "startline", "for": "edge"},
    {"id": "returnFrom", "attr.name": "returnFrom", "for": "edge"},
    {"id": "assumption", "attr.name": "assumption", "for": "edge"},
    {"id": "tokens", "attr.name": "tokens", "for": "edge"},
    {"id": "control", "attr.name": "control", "for": "edge"},
    {"id": "originfile", "attr.name": "originfile", "for": "edge", "default": "/home/hrishik/Misc/Tools/input/minepump_spec1_product10.cil.c"},
    {"id": "sourcecode", "attr.name": "sourcecode", "for": "edge"}
]


     # Add keys to GraphML
    for key_info in keys_info:
        key_element = ET.SubElement(graphml, "key", {"id": key_info["id"], "attr.name": key_info["attr.name"], "for": key_info["for"]})
        if "default" in key_info:
            default_element = ET.SubElement(key_element, "default")
            default_element.text = key_info["default"]

    # Add graph element
    graph = ET.SubElement(graphml, "graph", edgedefault="directed") 

    # Create entry node
    entry_node = ET.SubElement(graph, "node", id="N1")
    ET.SubElement(entry_node, "data", key="entry").text = "true"

    # Create nodes for loop heads, control true and control false
    node_id = 2  # Start from 2 as 1 is used for entry node
    edge_id = 0


    unique_loop_heads = {}
    for control_type, line_number, func in parsed_trace_data_list:
        if control_type == "reached_control":
            continue  # Skip creating nodes and edges for reached_control
        

        source_node_id = f"N{node_id}"
        node_id += 1
        target_node_id = f"N{node_id}"
        node_id += 1

        # Create nodes
        source_node = ET.SubElement(graph, "node", id=source_node_id)
        target_node = ET.SubElement(graph, "node", id=target_node_id)

        print (control_type, line_number, func, source_node_id, target_node_id)



        # If loop_head, make unique and set cyclehead
        if control_type == "loop_head":
            if line_number not in unique_loop_heads:
                unique_loop_heads[line_number] = source_node_id
                ET.SubElement(source_node, "data", key="cyclehead").text = "true"
            else:
                # Use existing unique loop_head node
                source_node_id = unique_loop_heads[line_number]

        # Create edge
        edge = ET.SubElement(graph, "edge", id=f"E{edge_id}", source=source_node_id, target=target_node_id)
        ET.SubElement(edge, "data", key="startline").text = str(line_number)
        ET.SubElement(edge, "data", key="endline").text = str(line_number)
        
        # Set additional attributes based on control type
        if control_type == "loop_head":
            ET.SubElement(edge, "data", key="enterLoopHead").text = "true"
        elif control_type == "control_true":
            ET.SubElement(edge, "data", key="control").text = "condition-true"
        elif control_type == "control_false":
            ET.SubElement(edge, "data", key="control").text = "condition-false"

        edge_id += 1



    return graphml



def write_graphml_to_file(graphml, output_file):
    rough_string = ET.tostring(graphml, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_string = reparsed.toprettyxml(indent="  ")

    with open(output_file, 'w') as file:
        file.write(pretty_string)





#Define main function and call parse_trace_file function
def main():
    #Read trace file path from command line
    trace_file_path = sys.argv[1]
    parsed_trace_data,parsed_trace_data_list = parse_trace_file(trace_file_path)
    #parsed_trace_data = parse_trace_file(trace_file_path)
    graphml_structure = create_graphml_structure(parsed_trace_data, parsed_trace_data_list)
    write_graphml_to_file(graphml_structure, "witness.graphml")
    print ("GraphML file created successfully")
    

    for key, value in parsed_trace_data.items():
        print(f"{key}: {value}")
        print("\n")

    # for item in parsed_trace_data_list:
    #     print(item)

if __name__ == "__main__":
    main()


