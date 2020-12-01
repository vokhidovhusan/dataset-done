import os
import sys
import argparse
import utils


def main(args):

    classes = args.classes
    print('classes: ' + str(classes))
    
    for sub in args.sub_dir:
        
        path = os.path.join(args.root_dir, sub)
        print(path)
        # remove existing txt files for annotation
        utils.remove_annot_files(path)
        
        for _, _, f in os.walk(os.path.join(path, 'Annotations')):
            for file in f:
                if '.json' in file:
                    filename = file.replace('.json', '')
                    print(file)
                    utils.convert_annotation(path, filename, classes)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='/home/husan/lightvision/datasets/')
    parser.add_argument('--sub_dir', action='append', type=str, help='root of VOC development kit')
    parser.add_argument('--classes', action='append', type=str,
                        help='list of classes for subset', default =
                        [
                            # 'bus', 'moto',
                            # '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B'
                            'rnplate',
                            # 'rnplate01',
                            # 'rnplate02',
                            # 'rnplate03',
                            # 'rnplate04',
                            # 'rnplate05',
                            # 'rnplate06',
                            # 'rnplate07',
                            # 'rnplate08',
                            # 'rnplate09',
                            # 'rnplate10',
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
