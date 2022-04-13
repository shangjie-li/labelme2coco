import json
import os
import sys
from collections import defaultdict

usage_text = """
This script splits one coco annotation file into two for training and validation, respectively.

Usage: python split_sets.py input_file output_name1 output_name2

For instance,
    python split_sets.py instances.json instances_train.json instances_val.json
"""

fields_to_combine = ['images', 'annotations']
fields_to_steal   = ['categories']

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(usage_text)
        exit()

    in_file = sys.argv[1]
    out_file1 = sys.argv[2]
    out_file2 = sys.argv[3]

    out1 = {x: [] for x in fields_to_combine}
    out2 = {x: [] for x in fields_to_combine}

    print('Loading set %s...' % in_file)
    with open(in_file, 'r') as f:
        set_json = json.load(f)
    
    for field in fields_to_steal:
        out1[field] = set_json[field]
        out2[field] = set_json[field]
    
    print('Building image index...')
    image_idx = {x['id']: x for x in set_json['images']}

    print('Collecting annotations...')
    anns_idx = defaultdict(lambda: [])

    for ann in set_json['annotations']:
        anns_idx[ann['image_id']].append(ann)
    
    export_ids = list(image_idx.keys())
    export_ids.sort()
    export1_ids = []
    export2_ids = []
    for _id in export_ids:
        if _id % 3 != 0:
            export1_ids.append(_id)
        else:
            export2_ids.append(_id)
    
    print('Splitting....')
    print('The number of samples in %s is %d.' % (out_file1, len(export1_ids)))
    print('The number of samples in %s is %d.' % (out_file2, len(export2_ids)))
    for _id in export1_ids:
        out1['images'].append(image_idx[_id])
        out1['annotations'] += anns_idx[_id]
    for _id in export2_ids:
        out2['images'].append(image_idx[_id])
        out2['annotations'] += anns_idx[_id]
    print('Done.\n')

    print('Saving result...')
    with open(out_file1, 'w') as f:
        json.dump(out1, f, indent=4)
    with open(out_file2, 'w') as f:
        json.dump(out2, f, indent=4)
