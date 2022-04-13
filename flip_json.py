import argparse
import json
import numpy as np
import glob
import sys, os
from pathlib import Path

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description='Flip JSON')
    parser.add_argument('--input_root', default='labels', type=str,
                        help='Input root directory path to json files.')
    parser.add_argument('--output_root', default='labels_refined', type=str,
                        help='Output root directory path to json files.')

    global args
    args = parser.parse_args(argv)

class json2json(object):
    def __init__(self, input_root, output_root):
        '''
        Args:
            input_root (str): input root directory path to json files (labelme format)
            output_root (str): output root directory path to json files (labelme format)
        '''
        self.input_root = input_root
        self.output_root = output_root

        self.save_json()
        
    def save_json(self):
        labelme_json = glob.glob(os.path.join(self.input_root, '*.json'))
        num = len(labelme_json)
        for idx, json_file in enumerate(labelme_json):
            print('Processing: %d / %d...' % (idx + 1, num))
            with open(json_file, 'r') as fp:
                data = json.load(fp)
                img_h = data['imageHeight']
                img_w = data['imageWidth']
                
                for shape in data['shapes']:
                    points = np.array(shape['points'])
                    points[:, 0] = img_w - points[:, 0]
                    shape['points'] = points.tolist()

            save_json_path = os.path.join(self.output_root, json_file.split('/')[-1])
            print('Saving output json file to: %s' % save_json_path)
            json.dump(data, open(save_json_path, 'w'), indent=1)


if __name__ == '__main__':
    parse_args()
    print('Input root directory:\n %s' % Path(args.input_root).resolve())
    print('Output root directory:\n %s' % Path(args.output_root).resolve())
    if not os.path.exists(args.output_root):
        os.mkdir(args.output_root)
    
    print()
    
    json2json(args.input_root, args.output_root)
