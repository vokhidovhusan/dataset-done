import os
import sys
import argparse
import json
from pathlib import Path
import utils


def main(args):

    for sub in args.sub_dir:
        path = os.path.join(args.root_dir, sub)
        print(path)
        label_count_path = Path(os.path.join(path, 'labelCount'))
        label_count_path.mkdir(exist_ok=True)
        path_count_sublabels = '{}/{}.json'.format(label_count_path, 'count_sublabels')
        path_count_labels = '{}/{}.json'.format(label_count_path, 'count_labels')
        path_labels_filenames = '{}/{}.json'.format(label_count_path, 'labels_filenames')
        path_differenct_lables = '{}/{}.json'.format(label_count_path, 'differenct_lables')
        path_labels = '{}/{}.json'.format(path, 'labels')

        # remove existing txt files for annotation
        # utils.remove_label_json_files(path_count_detail_labels)
        # utils.remove_label_json_files(path_count_labels)

        labels_filenames_dict = {}
        differenct_lables_dict = {}
        count_json = 0
        count_img = 0
        sublabels_list = []
        for _, _, f in os.walk(os.path.join(path)):
            for file in f:
                if args.file_ext in file:

                    filename = file.replace(args.file_ext, '')
                    print(filename)
                    print(path)
                    if args.file_ext == '.json':
                        file_labels = utils.get_lables(Path(os.path.join(path, 'Annotations')), filename,args.file_ext)
                    elif args.file_ext == '.xml':
                        file_labels = utils.get_lables_x(Path(os.path.join(path, 'Annotations')), filename,args.file_ext)
                    else:
                        continue
                    print(file_labels)
                    if len(file_labels) <= 0:
                        continue
                    print(os.path.join(path, file.replace(args.file_ext, '.jpg')))
                    # if os.path.exists(os.path.join(path,  file)) and\
                    #         os.path.exists(os.path.join(path,  file.replace(args.file_ext, '.jpg'))):
                    #     if(utils.move_file_to_directories(path, 'JPEGImages', file.replace(args.file_ext, '.jpg'))):
                    #         count_json += 1
                    #     if(utils.move_file_to_directories(path, 'Annotations', file)):
                    #         count_img += 1
                    # else:
                    #    # print('file not found "{}/"'.format(file))
                    #     continue

                    if len(file_labels) > 1:
                        contains_duplicates = any(file_labels.count(element) > 1 for element in file_labels)
                        if not contains_duplicates:
                            print(filename)
                            differenct_lables_dict[filename] = file_labels

                    for label in file_labels:
                        if label in labels_filenames_dict:
                            name_list = labels_filenames_dict.get(label)
                            name_list.extend([filename])
                            labels_filenames_dict[label] = name_list
                        else:
                            labels_filenames_dict[label] = [filename]

                    sublabels_list.extend(file_labels)



        # print(labels_filenames_dict)

        count_sublabel_dict = {i: sublabels_list.count(i) for i in sublabels_list}
        # print(count_sublabel_dict)
        count_sublabel_dict = dict(sorted(count_sublabel_dict.items()))

        label_list = [i.partition("_")[0] for i in sublabels_list]
        count_label_dict = {i: label_list.count(i) for i in label_list}
        count_label_dict = dict(sorted(count_label_dict.items()))
        # print(count_label_dict)


        labels = list(dict.fromkeys(label_list))
        # print(labels)
        sublabels = list(dict.fromkeys(count_label_dict))
        # print(sublabels)


        # print(count_json)
        # print(count_img)
        with open(path_count_sublabels, 'a+') as out_file:
            print('writing into: ', path_count_sublabels)
            out_file.write(json.dumps(count_sublabel_dict))

        with open(path_count_labels, 'a+') as out_file:
            print('writing into: ', path_count_labels)
            out_file.write(json.dumps(count_label_dict))

        with open(path_labels_filenames, 'a+') as out_file:
            print('writing into: ', path_labels_filenames)
            out_file.write(json.dumps(labels_filenames_dict))
        
        with open(path_differenct_lables, 'a+') as out_file:
            print('writing into: ', path_differenct_lables)
            out_file.write(json.dumps(differenct_lables_dict))


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='/home/husan/projects/domestic_waste/yolov5-train/datasets/')
    parser.add_argument('--sub_dir', action='append', type=str, help='root of VOC development kit')
    parser.add_argument('--file_ext', type=str, help='file extension', default='.xml')
    return parser.parse_args(argv)







if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
