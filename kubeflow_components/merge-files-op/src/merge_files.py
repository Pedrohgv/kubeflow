from pathlib import Path
import os
from shutil import move
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--nested_folder', type=str, help='Input folder containing files on separate folders', required=True)
parser.add_argument('--merged_folder', type=str, help='Output Folder that will contain merged files.')

args = parser.parse_args()

nested_folder = args.nested_folder
merged_folder = args.merged_folder

print('Creating output folder...')
os.makedirs(merged_folder, exist_ok=True)

for f in Path(nested_folder).glob('*/*'):

    move(f, merged_folder + '/' + f.name)




