#!/usr/bin/env python3

"""
Traverses a directory structure filled with
  Other directories, or symlinks to other directories
  Files, or symlinks to files

Gathers all files (or symlinks to), and transcodes to mp3

Starting point (input files) is provided as CWD
Output directory is provided via 1st positional argument
"""

import subprocess
import argparse
from pathlib import Path

OUTPUT_DIR = Path('/dev/null')  # Gets modified later
COUNTS = {
    'flac': 0,
    'm4a': 0,
    ''
}


def calculate_alpha_index(count: int):
    distance = ord('z') - ord('a') + 1
    index = chr(ord('a') + count % distance)
    count //= distance
    while count > 0:
        index = chr(ord('a') + count % distance) + index
        count //= distance
    return index


class MovingIndex:
    def __init__(self, starting_point: int):
        self.index = starting_point

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        # TODO if self.index exceeds some upper limit, raise StopIteration
        return calculate_alpha_index(self.index - 1)


current_index = MovingIndex(1)
weird_index = MovingIndex(25 * (26 ** 2) + 25 * (26 ** 1))


class NoHandlerForExtension(Exception):
    # TODO class should have 'extension' field to store which extension triggered the exception
    pass


class FileNotProcessed(Exception):
    pass


def process_flac(item: Path):
    destination = OUTPUT_DIR / (next(current_index) + '.mp3')
    cmdline = 'flac -s -c -d {source} | lame --silent --preset insane - {dest}'.format(source=item, dest=destination)
    subprocess.run(cmdline, shell=True, check=True)


def process_m4a(item: Path):
    destination = OUTPUT_DIR / (next(weird_index) + '.m4a')
    cmdline = 'cp {source} {dest}'.format(source=item, dest=destination)
    subprocess.run(cmdline, shell=True, check=True)


def process_file(item: Path):
    # Assertion: item.is_file()
    """
    Determine the file type (by extension lookup) and take appropriate action
    """
    if item.suffix == '.flac':
        COUNTS['flac'] += 1
        process_flac(item)
    elif item.suffix == '.m4a':
        COUNTS['m4a'] += 1
        process_m4a(item)
    else:
        raise NoHandlerForExtension(item.suffix)


def process_dir(dir: Path):
    for item in dir.iterdir():
        if item.is_dir():
            process_dir(item)
        elif item.is_file():
            try:
                process_file(item)
            except Exception as e:
                print("Couldn't process file {}".format(item))
        else:
            print("Couldn't process entry {}".format(item))


def print_report():
    print()
    for k, v in COUNTS.items():
        print("{}:\t{}".format(k, v))


def main():
    global OUTPUT_DIR
    parser = argparse.ArgumentParser()
    parser.add_argument('outdir')
    namespace = parser.parse_args()
    OUTPUT_DIR = Path(namespace.outdir)
    cwd = Path.cwd()
    process_dir(cwd)
    print_report()


if __name__ == "__main__":
    main()
