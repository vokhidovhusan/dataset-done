import os
import sys
import argparse
import utils


from pathlib import Path
def main(args):
    
    for sub in args.sub_dir:
        
        path = os.path.join(args.root_dir, sub)
        print(path)
        # Open the file with read only permit
        f = open('{}/{}.txt'.format(path, args.operation[0]), "r")
        # use readlines to read all lines in the file
        # The variable "lines" is a list containing all lines in the file
        lines = f.readlines()
        count = 0
        # close the file after reading the lines.
        for line in lines:
            print(line[:-1])            
            if os.path.exists(line[:-1]):
                bool_success = True
                p = Path(os.path.join(path, 'JPEGImages_{}'.format(args.operation[0])))
                p.mkdir(exist_ok=True)
                file_name = line.rsplit('/', 1)[-1][:-1]   
                print(file_name)             
                if(utils.copy_file_to_directories_full_path(line[:-1], '{}/{}'.format(p, file_name))):
                    count += 1                
                # else:
                #     # print('file not copy "{}/"'.format(file))
                #     continue
        print(len(lines))
        f.close()
        # # remove existing txt files for annotation
        # utils.remove_annot_files(path)
        
        # for _, _, f in os.walk(os.path.join(path, 'Annotations')):
        #     for file in f:
        #         if '.json' in file:
        #             filename = file.replace('.json', '')
        #             print(file)
        #             utils.convert_annotation(path, filename, classes)


def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='/home/husan/lightvision/datasets/')
    parser.add_argument('--sub_dir', action='append', type=str, help='root of VOC development kit')
    parser.add_argument('--operation', action='append', type=str, help='test or train')
    return parser.parse_args(argv)







if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
