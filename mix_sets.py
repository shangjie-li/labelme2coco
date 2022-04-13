import json
import os
import sys
from collections import defaultdict

usage_text = """
This script creates a coco annotation file by mixing one or more existing annotation files.

Usage: python mix_sets.py output_name [set1 range1 [set2 range2 [...]]]

For instance,
    python mix_sets.py trainval35k.json train2014.json : val2014.json :-5000

This will create an trainval35k.json file with all images and corresponding annotations
from train2014.json and the first 35000 images from val2014.json.

You can also specify only one set:
    python mix_sets.py minival5k.json val2014.json -5000:

This will take the last 5k images from val2014.json and put it in minival5k.json.
"""

fields_to_combine = ['images', 'annotations']
fields_to_steal   = ['categories']

if __name__ == '__main__':
    if len(sys.argv) < 4 or len(sys.argv) % 2 != 0:
        print(usage_text)
        exit()

    out_file = sys.argv[1]
    sets = sys.argv[2:]
    sets = [(sets[2*i], sets[2*i+1]) for i in range(len(sets)//2)]

    out = {x: [] for x in fields_to_combine}

    for idx, (set_path, range_str) in enumerate(sets):
        print('Loading set %s...' % set_path)
        with open(set_path, 'r') as f:
            set_json = json.load(f)

        # "Steal" some fields that don't need to be combined from the first set
        if idx == 0:
            for field in fields_to_steal:
                out[field] = set_json[field]
        
        print('Building image index...')
        image_idx = {x['id']: x for x in set_json['images']}

        print('Collecting annotations...')
        anns_idx = defaultdict(lambda: [])

        for ann in set_json['annotations']:
            anns_idx[ann['image_id']].append(ann)

        export_ids = list(image_idx.keys())
        export_ids.sort()
        export_ids = eval('export_ids[%s]' % range_str, {}, {'export_ids': export_ids})

        print('Adding %d images...' % len(export_ids))
        for _id in export_ids:
            out['images'].append(image_idx[_id])
            out['annotations'] += anns_idx[_id]

        print('Done.\n')

    print('Saving result...')
    with open(out_file, 'w') as f:
        json.dump(out, f)
