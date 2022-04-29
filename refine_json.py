import argparse
import json
import numpy as np
import glob
import sys, os
from pathlib import Path

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description='Refine JSON')
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
        labelme_json.sort()
        num = len(labelme_json)
        for idx, json_file in enumerate(labelme_json):
            print('Processing: %d / %d...' % (idx + 1, num))
            with open(json_file, 'r') as fp:
                data = json.load(fp)
                data['version'] = "3.16.2"
                
                for shape in data['shapes']:
                    shape['line_color'] = None
                    shape['fill_color'] = None
                    if 'group_id' in shape:
                        del shape['group_id']
                
                data['lineColor'] = [0, 255, 0, 128]
                data['fillColor'] = [255, 0, 0, 128]
                data['imageData'] = None
                
                if 'summary' in data:
                    del data['summary']
                if '/' in data['imagePath']:
                    data['imagePath'] = data['imagePath'].split('/')[-1]
                if data['imageHeight'] == 0 and data['imageWidth'] == 0:
                    try:
                        import matplotlib.pyplot as plt
                        img_file = json_file.replace(
                            os.path.splitext(json_file)[1], os.path.splitext(data['imagePath'])[1])
                        img = plt.imread(img_file)
                        data['imageHeight'], data['imageWidth'], _ = img.shape
                    except:
                        pass

            save_json_path = os.path.join(self.output_root, json_file.split('/')[-1])
            print('Saving output json file to: %s' % save_json_path)
            json.dump(data, open(save_json_path, 'w'), indent=1)


if __name__ == '__main__':
    parse_args()
    print('Input root directory:\n %s' % Path(args.input_root).resolve())
    print('Output root directory:\n %s' % Path(args.output_root).resolve())
    assert os.path.exists(args.input_root), 'Directory Not Found: %s' % args.input_root
    if not os.path.exists(args.output_root):
        os.mkdir(args.output_root)
    
    print()
    
    json2json(args.input_root, args.output_root)
