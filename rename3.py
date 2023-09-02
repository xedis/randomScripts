#! /bin/python3
import os
import hashlib
import argparse
import datetime
import logging
from pathlib import Path

parser = argparse.ArgumentParser(description='Process some files.')
parser.add_argument('--dir', type=str, help='The directory to be processed')
parser.add_argument('--ext', type=str, help='The file extension to be processed')
args = parser.parse_args()

# Ensure arguments are provided
if not args.dir or not args.ext:
    print("You must provide --dir and --ext arguments.")
    exit(1)

# Set up logging
log_file = Path(__file__).parent / 'file_renamer.log'
logging.basicConfig(filename=log_file, level=logging.INFO)

def calculate_hash(filename, block_size=65536):
    hasher = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            hasher.update(block)
    return hasher.hexdigest()

def rename_files(directory, extension):
    special_strings = ['before-color-correction', 'before-highres-fix', 'mask']
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(extension):
                old_name = os.path.join(foldername, filename)
                creation_time = os.path.getctime(old_name)
                modified_time = os.path.getmtime(old_name)
                oldest_time = min(creation_time, modified_time)
                date_string = datetime.datetime.fromtimestamp(oldest_time).strftime('%Y%m%d.%H%M%S')
                filehash = calculate_hash(old_name)
                special_string = [s for s in special_strings if s in filename]
                special_string = '-' + special_string[0] if special_string else ''
                new_name = os.path.join(foldername, date_string + '-' + filehash + special_string + extension)
                if not os.path.exists(new_name):
                    os.rename(old_name, new_name)
                    logging.info(f'Renamed file {old_name} to {new_name}')
                else:
                    i = 1
                    while os.path.exists(new_name + '-' + str(i)):
                        i += 1
                    os.rename(old_name, new_name + '-' + str(i))
                    logging.info(f'Renamed file {old_name} to {new_name}-{i}')

rename_files(args.dir, args.ext)
