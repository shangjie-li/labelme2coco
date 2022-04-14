import argparse
import json
import os
import shutil
from tqdm import tqdm
import numpy as np
from pathlib import Path

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description='COCO2YOLO')
    parser.add_argument('--json_file', default='instances_train2017.json', type=str,
                        help='Input annotation file (coco form).')
    parser.add_argument('--output_dir', default='labels', type=str,
                        help='Output directory path.')
    parser.add_argument('--use_label_map', action='store_true',
                        help='Whether or not to use COCO 91to80 label map.')

    global args
    args = parser.parse_args(argv)

COCO_LABEL_MAP = { 1:  1,  2:  2,  3:  3,  4:  4,  5:  5,  6:  6,  7:  7,  8:  8,
                   9:  9, 10: 10, 11: 11, 13: 12, 14: 13, 15: 14, 16: 15, 17: 16,
                  18: 17, 19: 18, 20: 19, 21: 20, 22: 21, 23: 22, 24: 23, 25: 24,
                  27: 25, 28: 26, 31: 27, 32: 28, 33: 29, 34: 30, 35: 31, 36: 32,
                  37: 33, 38: 34, 39: 35, 40: 36, 41: 37, 42: 38, 43: 39, 44: 40,
                  46: 41, 47: 42, 48: 43, 49: 44, 50: 45, 51: 46, 52: 47, 53: 48,
                  54: 49, 55: 50, 56: 51, 57: 52, 58: 53, 59: 54, 60: 55, 61: 56,
                  62: 57, 63: 58, 64: 59, 65: 60, 67: 61, 70: 62, 72: 63, 73: 64,
                  74: 65, 75: 66, 76: 67, 77: 68, 78: 69, 79: 70, 80: 71, 81: 72,
                  82: 73, 84: 74, 85: 75, 86: 76, 87: 77, 88: 78, 89: 79, 90: 80}

class coco2yolo(object):
    def __init__(self, json_file, output_dir='labels', label_map=None):
        '''
        '''
        self.json_file = json_file
        self.output_dir = output_dir
        self.label_map = label_map
        
        self.save_txt()
        
    def save_txt(self):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        else:
            shutil.rmtree(self.output_dir)
            os.mkdir(self.output_dir)
        
        with open(self.json_file) as f:
            data = json.load(f)
        
        images = {'%g' % x['id']: x for x in data['images']}
        set_file = 'set.txt'
        with open(set_file, 'w') as fp:
            for _id, val in images.items():
                fp.write('../../images/' + val['file_name'] + '\n')
        
        for x in tqdm(data['annotations'], desc=f'Annotations {self.json_file}'):
            if x['iscrowd']:
                continue
            
            img = images['%g' % x['image_id']]
            h, w, f = img['height'], img['width'], img['file_name']
            
            # The COCO box format is [top left x, top left y, width, height]
            box = np.array(x['bbox'], dtype=np.float64)
            box[:2] += box[2:] / 2 # xy top-left corner to center
            box[[0, 2]] /= w # normalize x
            box[[1, 3]] /= h # normalize y
            
            if box[2] > 0 and box[3] > 0: # if w > 0 and h > 0
                try:
                    if self.label_map:
                        cls = self.label_map[x['category_id']] - 1
                    else:
                        cls =  x['category_id'] - 1
                    line = cls, *box
                    p = Path(os.path.join(self.output_dir, f)).with_suffix('.txt')
                    with open(p, 'a') as fp:
                        fp.write(('%g ' * len(line)).rstrip() % line + '\n')
                except KeyError:
                    continue

if __name__ == '__main__':
    parse_args()
    print('Input annotation file (coco form):\n %s' % Path(args.json_file).resolve())
    print('Output directory path:\n %s' % Path(args.output_dir).resolve())
    
    print()
    
    if args.use_label_map:
        coco2yolo(args.json_file, args.output_dir, COCO_LABEL_MAP)
    else:
        coco2yolo(args.json_file, args.output_dir)
