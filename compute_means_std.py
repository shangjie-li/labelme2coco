try:
    import cv2
except:
    import sys
    sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
    import cv2

import os
import sys
import numpy as np
import glob

usage_text = """
This script compute MEANS and STD of a dataset.

Usage: python compute_means_std.py dataset_root

For instance,
    python compute_means_std.py /home/lishangjie/data/KITTI/kitti_dual/images
"""

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(usage_text)
        exit()

    dataset_root = sys.argv[1]
    files_of_png = glob.glob(os.path.join(dataset_root, '*.png'))
    files_of_jpg = glob.glob(os.path.join(dataset_root, '*.jpg'))
    files_of_jpeg = glob.glob(os.path.join(dataset_root, '*.jpeg'))
    files = files_of_png + files_of_jpg + files_of_jpeg
    num = len(files)
    
    mean_rs, mean_gs, mean_bs = [], [], []
    std_rs, std_gs, std_bs = [], [], []
    
    for idx in range(num):
        name = os.path.basename(files[idx])
        img = cv2.imread(os.path.join(dataset_root, name))
        #~ img = cv2.imread(os.path.join(dataset_root, name), cv2.IMREAD_GRAYSCALE)[:, :, None].repeat(3, axis=-1)
        print('Reading: %d / %d...' % (idx + 1, num))
        
        mean_bs.append(np.mean(img[:, :, 0]).item())
        mean_gs.append(np.mean(img[:, :, 1]).item())
        mean_rs.append(np.mean(img[:, :, 2]).item())
        
        std_bs.append(np.std(img[:, :, 0]).item())
        std_gs.append(np.std(img[:, :, 1]).item())
        std_rs.append(np.std(img[:, :, 2]).item())
    
    mean_r = round(np.mean(mean_rs).item(), 2)
    mean_g = round(np.mean(mean_gs).item(), 2)
    mean_b = round(np.mean(mean_bs).item(), 2)
    
    std_r = round(np.mean(std_rs).item(), 2)
    std_g = round(np.mean(std_gs).item(), 2)
    std_b = round(np.mean(std_bs).item(), 2)
    
    mean_rgb = (mean_r, mean_g, mean_b)
    std_rgb = (std_r, std_g, std_b)
    
    print()
    print('MEANS (RGB):', mean_rgb)
    print('STD (RGB):', std_rgb)
