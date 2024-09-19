import argparse
import re

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    parser = argparse.ArgumentParser(description='Process a ctp text file.')
    parser.add_argument('file', type=str, help='The path to the text file')
    args = parser.parse_args()

    ctp_file = read_file(args.file)
    if ctp_file:
        unique_commands = find_unique_commands(ctp_file)
        print(f"Unique commands:")
        for command in unique_commands:
            print(command)

def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")

def find_unique_commands(content):
    unique_commands = set()
    command_pattern = r't="([^"]+)"\s*n="([^"]+)">(.+)</e>'

    for line in content.splitlines():
        match = re.search(command_pattern, line)
        if match:
            # Extract the label and add it to the set
            unique_commands.add(match.group(3))
    return unique_commands

if __name__ == '__main__':
    main()

