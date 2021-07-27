import glob
import os
import pickle
import xml.etree.ElementTree as ET
from os import listdir, getcwd
from os.path import join
import argparse
from pathlib import Path
import shutil

parser = argparse.ArgumentParser(description='Converts annotation from Pascal to Yolo format')

parser.add_argument('--pascal_folder', type=str, help='Path of labeled images on Pascal format.', required=True)
parser.add_argument('--yolo_folder', type=str, help='Path to output labeled images on Yolo format after conversion.', required=True)
parser.add_argument('--classes', nargs='+', help='Classes to convert to Yolo format.', required=True)

args = parser.parse_args()

def getImagesInDir(dir_path):
    image_list = []
    for filename in glob.glob(dir_path + '/*.png'):
        image_list.append(filename)
    for filename in glob.glob(dir_path + '/*.jpg'):
        image_list.append(filename)
    return image_list

def convert(size, box):
    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0 - 1
    y = (box[2] + box[3])/2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

def convert_annotation(dir_path, output_path, image_path, classes):
    basename = os.path.basename(image_path)
    basename_no_ext = os.path.splitext(basename)[0]

    in_file = open(dir_path + '/' + basename_no_ext + '.xml')
    out_file = open(output_path + '/' + basename_no_ext + '.txt', 'w')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

pascal_folder = args.pascal_folder
yolo_folder = args.yolo_folder
classes = args.classes

print(pascal_folder)
print(yolo_folder)
print(classes)


# creates output folder
print('Creating output folder...')
os.makedirs(yolo_folder, exist_ok=True)


image_paths = getImagesInDir(pascal_folder)

print(image_paths[:3])


for image_path in image_paths:

    convert_annotation(
        dir_path=pascal_folder,
        output_path=yolo_folder,
        image_path=image_path,
        classes=classes
    )

    shutil.copy(image_path, yolo_folder)
    
print("Finished processing: " + yolo_folder)

