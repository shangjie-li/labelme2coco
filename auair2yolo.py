import argparse
import json
import os
import shutil
from tqdm import tqdm
import numpy as np
from pathlib import Path

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description='AUAIR2YOLO')
    parser.add_argument('--json_file', default='annotations.json', type=str,
                        help='Input annotation file (auair form).')
    parser.add_argument('--output_dir', default='labels', type=str,
                        help='Output directory path.')

    global args
    args = parser.parse_args(argv)
    
AUAIR_CATEGORIES = ['Human', 'Car', 'Truck', 'Van', 'Motorbike', 'Bicycle', 'Bus', 'Trailer']

class auair2yolo(object):
    def __init__(self, json_file, output_dir='labels'):
        '''
        '''
        self.json_file = json_file
        self.output_dir = output_dir
        
        self.save_txt()
        
    def save_txt(self):
        if not os.path.exists(self.output_dir):
            os.mkdir(self.output_dir)
        else:
            shutil.rmtree(self.output_dir)
            os.mkdir(self.output_dir)
        
        with open(self.json_file) as f:
            data = json.load(f)
        
        image_id = 0
        train_set_file = 'train.txt'
        with open(train_set_file, 'w') as fp:
            fp.truncate(0)
        val_set_file = 'val.txt'
        with open(val_set_file, 'w') as fp:
            fp.truncate(0)
        
        for x in tqdm(data['annotations'], desc=f'Annotations {self.json_file}'):
            image_id += 1
            image_name = x['image_name']
            w, h = x['image_width:'], x['image_height']
            if image_id % 3 != 0:
                with open(train_set_file, 'a') as fp:
                    fp.write('../../images/' + image_name + '\n')
            else:
                with open(val_set_file, 'a') as fp:
                    fp.write('../../images/' + image_name + '\n')
            
            boxes = [[b['left'], b['top'], b['width'], b['height']] for b in x['bbox']]
            classes = [b['class'] for b in x['bbox']]
            
            boxes = np.array(boxes, dtype=np.float64)
            boxes[:, :2] += boxes[:, 2:] / 2 # xy top-left corner to center
            boxes[:, 0::2] /= w # normalize x
            boxes[:, 1::2] /= h # normalize y
            for idx, box in enumerate(boxes):
                if box[2] > 0 and box[3] > 0: # if w > 0 and h > 0:
                    line = classes[idx], *box
                    p = Path(os.path.join(self.output_dir, image_name)).with_suffix('.txt')
                    with open(p, 'a') as fp:
                        fp.write(('%g ' * len(line)).rstrip() % line + '\n')
                        
if __name__ == '__main__':
    parse_args()
    print('Input annotation file (auair form):\n %s' % Path(args.json_file).resolve())
    print('Output directory path:\n %s' % Path(args.output_dir).resolve())
    
    print()
    
    auair2yolo(args.json_file, args.output_dir)
