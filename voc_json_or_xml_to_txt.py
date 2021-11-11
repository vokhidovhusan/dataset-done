import os
import sys
import argparse

from numpy.lib.type_check import imag
import utils


def main(args):

    classes = args.classes
    print('classes: ' + str(classes))
    img_count = 0
    for sub in args.sub_dir:
        
        path = os.path.join(args.root_dir, sub)
        print(path)
        # remove existing txt files for annotation
        utils.remove_annot_files(path)
        
        
        
        
        
        walk_path = os.path.join(path, 'Annotations')
        
        for _, _, f in os.walk(walk_path):
            for file in f:
                if not file.endswith(('.json','.xml')):
                    continue
                if '.json' in file:
                    filename = file.replace('.json', '')
                    if args.dataset_name == 'coco':                        
                        utils.convert_annotation(path, filename, classes)
                    if args.dataset_name == 'taco':
                        
                        print(file)
                        utils.convert_annotation_taco(path, filename, classes)

                if '.xml' in file:
                    filename = file.replace('.xml', '')
                    # print(file)
                    utils.convert_annotation_x(path, filename, classes)
                    img_count  +=  1
    print('image count: ', img_count)

def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='/home/husan/projects/domestic_waste/yolov5-train/datasets/')
    parser.add_argument('--sub_dir', action='append', type=str, help='root of VOC development kit')
    parser.add_argument('--dataset_name', default='coco', type=str, help='dataset name, for example: coco, taco')
    parser.add_argument('--classes', action='append', type=str,
                        help='list of classes for subset', default =
                        [
                            # 'bus', 'moto',
                            # '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', 'A', 'B', 'G', 'M','N'
                            '01', '02', '03', '04', '05', '06', '07'
                            # 'rnplate',
                            # 'rnplate00_01',
                            # 'rnplate00_02',
                            # 'rnplate00_03',
                            # 'rnplate00_04',
                            # 'rnplate00_05',
                            # 'rnplate00_06',
                            # 'rnplate00_07',
                            # 'rnplate00_08',
                            # 'rnplate00_09',
                            # 'rnplate00_10',
                            # 'aeroplane',
                            # 'bicycle',
                            # 'bird',
                            # 'boat',
                            # 'bottle',
                            # 'bus',
                            # 'car',
                            # 'cat',
                            # 'chair',
                            # 'cow',
                            # 'diningtable',
                            # 'dog',
                            # 'horse',
                            # 'motorbike',
                            # 'person',
                            # 'pottedplant',
                            # 'sheep',
                            # 'sofa',
                            # 'train',
                            # 'tvmonitor'
                        ])
    return parser.parse_args(argv)







if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
