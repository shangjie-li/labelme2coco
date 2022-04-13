import matplotlib.pyplot as plt # For WARNING: QApplication was not created in the main() thread.

try:
    import cv2
except:
    import sys
    sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
    import cv2

import pathlib as Path
import os
import argparse
import glob

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description='Flip Image')
    parser.add_argument('--input_root', default=None, type=str,
                        help='An input folder to images.')
    parser.add_argument('--output_root', default=None, type=str,
                        help='An output folder to images.')

    global args
    args = parser.parse_args(argv)

if __name__ == '__main__':
    parse_args()
    
    if args.input_root or args.output_root:
        if args.input_root is None or args.output_root is None:
            print('Error: args.input_root and args.output_root must be set at the same time!')
            exit()
        if not os.path.exists(args.output_root):
            os.mkdir(args.output_root)
    
    files_of_png = glob.glob(os.path.join(args.input_root, '*.png'))
    files_of_jpg = glob.glob(os.path.join(args.input_root, '*.jpg'))
    files_of_jpeg = glob.glob(os.path.join(args.input_root, '*.jpeg'))
    files = files_of_png + files_of_jpg + files_of_jpeg
    num = len(files)
    
    for idx in range(num):
        print('Processing: %d / %d...' % (idx + 1, num))
        
        input_name = os.path.basename(files[idx])
        print(input_name)
        img = cv2.imread(os.path.join(args.input_root, input_name))
        img = img[:, ::-1]
        
        cv2.imwrite(os.path.join(args.output_root, input_name), img)


