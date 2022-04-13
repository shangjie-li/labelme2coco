try:
    import cv2
except:
    import sys
    sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
    import cv2

import argparse
import json
import matplotlib.pyplot as plt
import numpy as np
import glob
import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import sys, os
from pathlib import Path
from shapely.geometry import Polygon

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description='Labelme2COCO')
    parser.add_argument('--images_root', default='images_and_labels', type=str,
                        help='Root directory path to images.')
    parser.add_argument('--labels_root', default='images_and_labels', type=str,
                        help='Root directory path to labelme json files.')
    parser.add_argument('--output_file', default='instances.json', type=str,
                        help='Output annotation file (coco form).')
    parser.add_argument('--class_map_file', default=None, type=str,
                        help='A file that provides a map from old class name to new class name.')
    parser.add_argument('--classes_file', default=None, type=str,
                        help='A file that provides a list of class names.')

    global args
    args = parser.parse_args(argv)

class labelme2coco(object):
    def __init__(self, images_root, labels_root, save_json_path, specified_classes=None, class_map=None):
        '''
        Args:
            images_root (str): root directory path to images
            labels_root (str): root directory path to labelme json files
            save_json_path (str): a path to save output json file
        '''
        self.images_root = images_root
        self.labels_root = labels_root
        self.save_json_path = save_json_path
        
        self.images = [] # for output json file
        self.categories = [] # for output json file
        self.annotations = [] # for output json file
        
        self.labels = [] # class names
        self.num_ann = {} # number of annoations for each class
        
        self.specified_classes = specified_classes
        if self.specified_classes is not None:
            for label in self.specified_classes:
                self.labels.append(label)
                self.categories.append(self.categorie(label))
                self.num_ann[label] = 0
        
        self.class_map = class_map
        
        self.ann_id = 1
        self.height = 0 # for generating mask
        self.width = 0 # for generating mask

        self.save_json()

    def data_transfer(self):
        labelme_json = glob.glob(os.path.join(self.labels_root, '*.json'))
        num = len(labelme_json)
        for idx, json_file in enumerate(labelme_json):
            print('Processing: %d / %d...' % (idx + 1, num))
            with open(json_file, 'r') as fp:
                data = json.load(fp)
                self.images.append(self.image(data, idx))
                
                for shape in data['shapes']:
                    try:
                        label = shape['label'] # class name from labelme json file
                        points = shape['points']
                        if self.class_map:
                            label = self.class_map[label] if label in self.class_map else label
                        
                        if self.specified_classes is None:
                            if label not in self.labels:
                                self.labels.append(label)
                                self.categories.append(self.categorie(label))
                                self.num_ann[label] = 0
                            self.annotations.append(self.annotation(points, label, idx))
                            self.ann_id += 1
                            self.num_ann[label] += 1
                        elif label in self.labels:
                            self.annotations.append(self.annotation(points, label, idx))
                            self.ann_id += 1
                            self.num_ann[label] += 1
                    except:
                        print('Warning: A shape is passed because of ValueError.')
                        
        print('\nAll class names:\n', self.labels)
        print('\nNumber of annoations for each class:')
        for key, val in self.num_ann.items():
            print(' %s: %d' % (key, val))

    def image(self, data, idx):
        image = {}
        img = cv2.imread(os.path.join(self.images_root, data['imagePath']), 0)
        height, width = img.shape[:2]
        image['height'] = height
        image['width'] = width
        image['id'] = idx + 1
        image['file_name'] = data['imagePath'].split('/')[-1]
        self.height = height
        self.width = width
        return image

    def categorie(self, label):
        categorie = {}
        categorie['supercategory'] = label
        categorie['id'] = self.labels.index(label) + 1
        categorie['name'] = label
        return categorie

    def annotation(self, points, label, idx):
        annotation = {}
        annotation['segmentation'] = [list(map(int, list(np.asarray(points).flatten())))]
        poly = Polygon(points)
        area = round(poly.area, 6)
        annotation['area'] = area
        annotation['iscrowd'] = 0
        annotation['image_id'] = idx + 1
        annotation['bbox'] = list(map(float, self.getbbox(points)))
        annotation['category_id'] = self.getcatid(label)
        annotation['id'] = self.ann_id
        return annotation

    def getbbox(self, points):
        mask = self.polygons_to_mask([self.height, self.width], points)
        return self.mask2box(mask)

    def getcatid(self, label):
        for categorie in self.categories:
            if label == categorie['name']:
                return categorie['id']
        return -1

    def polygons_to_mask(self, img_shape, polygons):
        mask = np.zeros(img_shape, dtype=np.uint8)
        mask = Image.fromarray(mask)
        xy = list(map(tuple, polygons))
        ImageDraw.Draw(mask).polygon(xy=xy, outline=1, fill=1)
        mask = np.array(mask, dtype=bool)
        return mask

    def mask2box(self, mask):
        index = np.argwhere(mask == 1)
        rows = index[:, 0]
        clos = index[:, 1]
        left_top_r = np.min(rows) # y
        left_top_c = np.min(clos) # x
        right_bottom_r = np.max(rows)
        right_bottom_c = np.max(clos)
        return [left_top_c, left_top_r, right_bottom_c - left_top_c, right_bottom_r - left_top_r] # [x1, y1, w, h]

    def data2coco(self):
        data_coco = {}
        data_coco['images'] = self.images
        data_coco['categories'] = self.categories
        data_coco['annotations'] = self.annotations
        return data_coco

    def save_json(self):
        self.data_transfer()
        self.data_coco = self.data2coco()
        
        print('\nSaving output json file to: %s' % self.save_json_path)
        json.dump(self.data_coco, open(self.save_json_path, 'w'), indent=4)
        
if __name__ == '__main__':
    parse_args()
    print('Root directory path to images:\n %s' % Path(args.images_root).resolve())
    print('Root directory path to labelme json files:\n %s' % Path(args.labels_root).resolve())
    print('Output annotation file (coco form):\n %s' % Path(args.output_file).resolve())
    
    if args.classes_file:
        path = args.classes_file
        assert os.path.exists(path), 'File does not exist: {}'.format(path)
        specified_classes = []
        for line in open(os.path.join(path)):
            if not line.isspace():
                name = line.strip()
                if '\\t' in name: name = ' '.join(name.split('\\t'))
                specified_classes.append(name)
    else:
        specified_classes = None
    print('\nSpecified class names:\n', specified_classes)
    
    if args.class_map_file:
        path = args.class_map_file
        assert os.path.exists(path), 'File does not exist: {}'.format(path)
        class_map = {}
        for line in open(os.path.join(path)):
            if not line.isspace():
                split = line.strip().split(':')
                old_name, new_name = split[0].strip(), split[1].strip()
                if '\\t' in old_name: old_name = ' '.join(name.split('\\t'))
                if '\\t' in new_name: new_name = ' '.join(name.split('\\t'))
                class_map[old_name] = new_name
    else:
        class_map = None
    print('\nClass map (old name -> new name):\n', class_map)
    
    print()
    
    labelme2coco(args.images_root, args.labels_root, args.output_file, specified_classes, class_map)


