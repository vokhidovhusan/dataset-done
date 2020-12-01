import os
import sys
import argparse
import utils



def main(args):

    for sub in args.sub_dir:
        path = os.path.join(args.root_dir, sub)
        print(path)
        # remove existing txt files for annotation
        # utils.remove_annot_files(path)
        count_json = 0
        count_img = 0
        for _, _, f in os.walk(os.path.join(path, 'Annotations')):

            for file in f:
                if '.json' in file:
                    # annotation_folder = Path(os.path.join(path, 'Annotation'))
                    # annotation_folder.mkdir(exist_ok=True)
                    #
                    # image_folder = Path(os.path.join(path, 'JPEGImages'))
                    # image_folder.mkdir(exist_ok=True)

                    filename = file.replace('.json', '')
                    print(file)
                    box_list = utils.get_box(os.path.join(path, 'Annotations'), filename)

                    success = utils.cut_label(path, filename, box_list, 'JPEGImages', '{}_rnplate'.format(sub))
                    print(success)
                    count_json += 1
                    if success:
                        # utils.move_file_to_directories(path, 'Annotations', 'Annotations_success', file)
                        # utils.move_file_to_directories(path, 'JPEGImages', 'JPEGImages_success', file.replace('.json', '.jpg'))
                        count_img += 1

    print(count_json)
    print(count_img)

def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='/home/husan/lightvision/datasets/label_cut/')
    parser.add_argument('--sub_dir', action='append', type=str, help='root of VOC development kit')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
