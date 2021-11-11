import os
import sys
import argparse
from pathlib import Path
import utils



def main(args):
    
    for sub in args.sub_dir:
        MODIFIED_FOLDER = 'modified_json'
        path = os.path.join(args.root_dir, sub)
        modified_json_path = Path(os.path.join(path, MODIFIED_FOLDER))
        modified_json_path.mkdir(exist_ok=True)
        print(path)

        # remove existing txt files for annotation
        # utils.remove_annot_files(path)
        for _, _, f in os.walk(path):
            for file in f:
                if '.json' in file:
                    filename = file.replace('.json', '')
                    print(file)
                    box_list = utils.check_json_parameters(path, filename, modified_dir = MODIFIED_FOLDER)
                        


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='/home/husan/lightvision/datasets/label_correction/')
    parser.add_argument('--sub_dir', action='append', type=str, help='root of VOC development kit')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
