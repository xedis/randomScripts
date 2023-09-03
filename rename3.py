#! bin/python3
"""
Renames and organizes image files into date/category structure.

Usage:
  python image_organizer.py --dir <ROOT_DIR> --ext <EXTENSION>
"""

import os
import re
from pathlib import Path
import hashlib
import argparse
import datetime
import logging

# Provide help text
parser = argparse.ArgumentParser(description='Rename and organize image files')
parser.add_argument('-d','--dir', required=True, help='Root directory of images')  
parser.add_argument('-e','--ext', required=True, help='File extension to process')
args = parser.parse_args()

# Set up logger
logger = logging.getLogger(__name__)  
logging.basicConfig(filename='image_organizer.log', level=logging.INFO)

# Configure paths
ROOT_DIR = Path('/opt/outputs') 

def calculate_hash(filepath):
    hasher = hashlib.sha256()
    with filepath.open('rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

def get_new_name(filepath, date_string, filehash, special_string):
    name = f'{date_string}-{filehash}{special_string}{filepath.suffix}'
    return filepath.with_name(name) 

def increment_name(filepath):
    name, ext = os.path.splitext(filepath.name)
    counter = 1
    while True:
        name_inc = f'{name}-{counter}{ext}'
        incremented_path = filepath.with_name(name_inc)
        if not incremented_path.exists():
            return incremented_path
        counter += 1
        
def rename_file(filepath):
    """
    Renames file to date-hash format.
    
    Parameters:
      filepath (Path): Path to file
    
    Returns:
      None
    """
    creation_time = filepath.stat().st_ctime
    modified_time = filepath.stat().st_mtime
    oldest_time = min(creation_time, modified_time)

    date_string = datetime.datetime.fromtimestamp(oldest_time).strftime('%Y%m%d.%H%M%S')  
    filehash = calculate_hash(filepath)
    
    special_strings = ['before-color-correction', 'before-highres-fix', 'mask']
    special_string = [s for s in special_strings if s in filepath.name]
    special_string = '-' + special_string[0] if special_string else ''
    
    new_name = get_new_name(filepath, date_string, filehash, special_string)
    if new_name.exists():
        new_name = increment_name(new_name)
    
    filepath.rename(new_name)
    logger.info(f'Renamed {filepath} to {new_name}')

def get_target_dir(filepath):
      """
    Determines target directory based on original location.
    
    Parameters:
      filepath (Path): Path to file
    
    Returns:
      target_dir (str): Relative path to target folder
    """
    filename = filepath.name
    date_match = re.match(r'(\d{8})', filename)
    date_str = date_match.group(1) if date_match else 'unknown'
    
    year = date_str[:4]
    month = date_str[4:6]

    rel_dir = os.path.relpath(filepath, ROOT_DIR)
    rel_dirs = rel_dir.split(os.sep)
    
    if 'extras' in rel_dirs:
        technique = 'extras' 
    elif 'grids' in rel_dirs:
        technique = 'grids'
    elif 'text' in rel_dirs:
        technique = 'text' 
    else:
        technique = rel_dirs[0]
        
    target_dir = os.path.join(year, year+'-'+month, technique)
    return target_dir

def move_file(filepath):
    target_dir = get_target_dir(filepath)  
    target_path = os.path.join(target_dir, filepath.name)
    os.makedirs(target_dir, exist_ok=True)
    filepath.rename(target_path)
   
if __name__ == '__main__': 
    for filepath in ROOT_DIR.rglob('*'):
        if filepath.is_file():
            rename_file(filepath)
            move_file(filepath)
