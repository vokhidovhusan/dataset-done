import os
import sys
import argparse
import json
from pathlib import Path
import utils


def main(args):

    for sub in args.sub_dir:
        path = os.path.join(args.root_dir, sub)
        label_count_path = Path(os.path.join(path, 'labelCount'))
        label_count_path.mkdir(exist_ok=True)
        path_ground_truth = '{}/{}.json'.format(label_count_path, 'ground_truth')
        path_differenct_lables = '{}/{}.json'.format(label_count_path, 'differenct_lables')
        differenct_lables_dict = {}
        labels_filenames_dict = {}
        
        for _, _, f in os.walk(os.path.join(path)):
            for file in f:
                if '.json' in file:                    
                    filename = file.replace('.json', '')
                    img_file = file.replace('.json', '.jpg')                    
                    file_labels = utils.get_lables(path, filename)
                    
                    if len(file_labels) <= 0:
                        continue
                    if len(file_labels) > 1:
                        contains_duplicates = any(file_labels.count(element) > 1 for element in file_labels)
                        if not contains_duplicates:
                            differenct_lables_dict[filename] = file_labels

                    for label in file_labels:                        
                        
                        if img_file in labels_filenames_dict:
                            name_list = labels_filenames_dict.get(img_file)
                            name_list.extend([label.partition("_")[2]])
                            labels_filenames_dict[img_file] = name_list
                        else:
                            labels_filenames_dict[img_file] = [label.partition("_")[2]]

        with open(path_ground_truth, 'a+') as out_file:
            print('writing into: ', path_ground_truth)
            out_file.write(json.dumps(labels_filenames_dict))
        
        with open(path_differenct_lables, 'a+') as out_file:
            print('writing into: ', path_differenct_lables)
            out_file.write(json.dumps(differenct_lables_dict))


        # Opening JSON file 
        with open(path_ground_truth) as json_file: 
            data = json.load(json_file) 
        
            # Print the type of data variable 
            print("Type:", type(data)) 
            for d in data:
                print(d)
                print(data[d])
        
            # Print the data of dictionary 
            # print("\nPeople1:", data['people1']) 
            # print("\nPeople2:", data['people2']) 


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='/home/husan/lightvision/')
    parser.add_argument('--sub_dir', action='append', type=str, help='root of VOC development kit')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
