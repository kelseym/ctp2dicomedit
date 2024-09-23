import argparse
import logging
import os
import re
import xml.etree.ElementTree as ET
from tokenize import String

function_pattern = r't="([^"]+)"\s*n="([^"]+)">(.+)</e>'


def main():
    parser = argparse.ArgumentParser(description='Convert a ctp xml file to DicomEdit format.')
    parser.add_argument('ctp', type=str, help='Path to ctp xml file.')
    parser.add_argument('dicom_edit', type=str, help='Path to DicomEdit output file.')

    args = parser.parse_args()

    if not args.ctp:
        logging.error("No content in ctp script file.")
    if os.path.exists(args.dicom_edit):
        overwrite = input(f"File {args.dicom_edit} already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            logging.info("File not overwritten.")
            return

    tree = ET.parse(args.ctp)
    ctp_root = tree.getroot()

    # If the file at the path 'dicom_edit' does not exist, create it
    with open(args.dicom_edit, 'w') as dicom_edit:
        dicom_edit.write('// Auto-generated CTP -> DicomEdit script\n')
        dicom_edit.write('// Generated by ctp2dicomedit\n')
        dicom_edit.write('version "6.6"\n')
        dicom_edit.write('\n')

    # Extract the dicom element commands
    dicom_element_commands = extract_dicom_element_commands(ctp_root)

    # Extract the global remove commands
    global_remove_commands = extract_global_remove_commands(ctp_root)

    # Extract the parameters
    parameters = extract_parameters(ctp_root)

    ## Write commands to DicomEdit file

    # Set the parameters
    set_parameters(parameters, args.dicom_edit)

    # Process the dicom element commands
    process_dicom_element_commands(dicom_element_commands, args.dicom_edit)

    # Process the global remove commands
    process_global_remove_commands(global_remove_commands, args.dicom_edit)




    logging.error('Unprocessed DICOM Element Commands:')
    for command in dicom_element_commands:
        logging.error(f"{command.tag} : {command.attrib} : {command.text}")
    logging.error('Unprocessed Global Remove Commands:')
    for command in global_remove_commands:
        logging.error(f"{command.tag} : {command.attrib} : {command.text}")
    print('Unprocessed Parameters:')
    for command in parameters:
        print(command.tag, command.attrib, command.text)
    if len(ctp_root) > 0:
        logging.error('Unrecognized Commands:')
        for child in ctp_root:
            logging.error(child.tag + " : " + str(child.attrib) + " : " + child.text)


def extract_dicom_element_commands(xml_content):
    dicom_element_commands = []
    for child in xml_content:
        if child.tag == "e":
            dicom_element_commands.append(child)
    for command in dicom_element_commands:
        xml_content.remove(command)
    return dicom_element_commands

def extract_global_remove_commands(xml_content):
    global_remove_commands = []
    for child in xml_content:
        if child.tag == "r":
            global_remove_commands.append(child)
    for command in global_remove_commands:
        xml_content.remove(command)
    return global_remove_commands

def extract_parameters(xml_content):
    parameters = []
    for child in xml_content:
        if child.tag == "p":
            parameters.append(child)
    for command in parameters:
        xml_content.remove(command)
    return parameters


def find_unique_functions(content):
    unique_functions = set()

    for line in content:
        match = re.search(function_pattern, line)
        if match:
            # Extract the label and add it to the set
            unique_functions.add(match.group(3))
    return unique_functions

def set_parameters(parameters, dicom_edit):
    # Set parameter values and write to DicomEdit file
    with open(dicom_edit, 'a') as dicom_edit:
        for command in parameters:
            dicom_edit.write(f'{command.attrib["t"]} := "{command.text}"\n')

def process_dicom_element_commands(dicom_element_commands, dicom_edit):
    with open(dicom_edit, 'a') as dicom_edit:
        for command in dicom_element_commands.copy():
            if(command.text == '@remove()'):
                print(f"Remove element: {command.attrib['n']}")
                dicom_edit.write(f'-{to_group_tag(command.attrib["t"])}     // remove {command.attrib["t"]}\n')
                dicom_element_commands.remove(command)
            elif (command.text == '@empty()'):
                print(f"Assign empty value to element: {command.attrib['n']}")
                dicom_edit.write(f'{to_group_tag(command.attrib["t"])} := ""     // Assign empty value to {command.attrib["t"]}\n')
                dicom_element_commands.remove(command)
            elif(command.text == '@incrementdate(this,@DATEINC)'):
                print(f"Increment element (if exists): {command.attrib['n']}")
                dicom_edit.write(f'{to_group_tag(command.attrib["t"])} ?= shiftDateByIncrement[ {to_group_tag(command.attrib["t"])}, DATEINC]'
                                 f' // Increment {command.attrib["t"]}\n')
                dicom_element_commands.remove(command)
            elif(command.text == '@hashuid(@UIDROOT,this)'):
                print(f"Hash UID element: {command.attrib['n']}")
                dicom_edit.write(f'{to_group_tag(command.attrib["t"])} ?= hashUID[ {to_group_tag(command.attrib["t"])}, UIDROOT ]     // Hash UID {command.attrib["t"]}\n')
                dicom_element_commands.remove(command)


def process_global_remove_commands(global_remove_commands, dicom_edit):
    with open(dicom_edit, 'a') as dicom_edit:
        for command in global_remove_commands.copy():
            if command.text == "Remove curves":
                print("Removing all curves")
                dicom_edit.write('-(50X@,XXXX)     // delete Curve Data\n')
                global_remove_commands.remove(command)
            elif command.text == "Remove private groups":
                print("Removing all private tags")
                dicom_edit.write('removeAllPrivateTags     // delete private tags\n')
                global_remove_commands.remove(command)
            elif command.text == "Remove overlays":
                print("Removing all overlays")
                dicom_edit.write('-(60X@,XXXX)     // delete overlays\n')
                global_remove_commands.remove(command)

def to_group_tag(grouptag):
    return f'({grouptag[0:4]},{grouptag[4:]})'

if __name__ == '__main__':
    main()

