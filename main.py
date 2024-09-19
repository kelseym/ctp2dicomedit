import argparse


# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    parser = argparse.ArgumentParser(description='Process a ctp text file.')
    parser.add_argument('file', type=str, help='The path to the text file')
    args = parser.parse_args()

    read_file(args.file)


def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            print(content)
    except FileNotFoundError:
        print(f"File not found: {file_path}")


if __name__ == '__main__':
    main()

