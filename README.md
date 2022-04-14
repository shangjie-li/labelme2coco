# labelme2coco

A Python tool for converting LABELME format into COCO format

## Requirements
 - Clone this repository
   ```
   git clone git@github.com:shangjie-li/labelme2coco.git
   ```
 - Install dependencies
   ```
   pip install shapely
   ```

## Usages
 - Convert LABELME formate into COCO format
   ```
   python labelme2coco.py --images_root=images --labels_root=labels --output_file=instances.json
   
   # If you want rename some classes in labels, just declare them in the class_map.txt and run
   python labelme2coco.py --images_root=images --labels_root=labels --output_file=instances.json --class_map_file=class_map.txt
   
   # If you want filter out some classes in labels, just declare what you want in the final_classes.txt and run
   python labelme2coco.py --images_root=images --labels_root=labels --output_file=instances.json --classes_file=final_classes.txt
   ```
 - Convert COCO format into YOLO format
   ```
   python coco2yolo.py --json_file=instances_train2017.json
   
   # If you want use COCO 91to80 label map, run
   python coco2yolo.py --json_file=instances_train2017.json --use_label_map
   ```
