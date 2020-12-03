import os
import sys
import argparse
import random
from pathlib import Path
from shutil import move, copyfile


def move_or_copy_file_to_other_directory(path, file_name, src='JPEGImages', dst='labels', copy=False, overwrite=True):
    src_path = Path(os.path.join(path, src))
    dst_path = Path(os.path.join(path, dst))
    dst_path.mkdir(exist_ok=True)
    try:
        # if copy:
        #     print('copying file {} to {}'.format(file_name, dst_path))
        # else:
        #     print('moving file {} to {}'.format(file_name, dst_path))

        if os.path.exists(os.path.join(dst_path, file_name)) and not overwrite:
            if copy:
                raise Exception('file exists! Can not copy the file to {}'.format(dst_path))
            else:
                raise Exception('file exists! Can not move the file to {}'. format(dst_path))
        else:
            if copy:
                copyfile(os.path.join(src_path, file_name), os.path.join(dst_path, file_name))
                print('file {} has been copied to {}/'.format(file_name, dst_path))
            else:
                move(os.path.join(src_path, file_name), os.path.join(dst_path, file_name))
                print('file {} has been moved to {}/'.format(file_name, dst_path))

    except IOError as e:
        if copy:
            print('unable to copy file %s' % e)
        else:
            print('unable to move file %s' % e)
        exit(1)

    except Exception as e:
        print('{}, {}'.format(e.args[0], e.args[1]))

    except:
        print('unexpected error:', sys.exc_info())
        exit(1)



def main(args):

    path = args.root_dir + '/{}/JPEGImages/'
    for sub in args.sub_dir:
        print('sub_dir: {}'.format(sub))
        img_path = []        
        for _, _, f in os.walk(path.format(sub)):
            for file in f:
                if '.txt' in file:
                    print(file)
                    image_file = file.replace('.txt', '.{}'.format(args.img_ext))
                    print(image_file)
                    img_path.append(path.format(sub) + image_file)
                    move_or_copy_file_to_other_directory(os.path.join(args.root_dir, sub), file)
       

        random.shuffle(img_path)

        with open('{}/{}/{}.txt'.format(args.root_dir, sub, 'train_val'), 'w+') as f:
            for p in img_path:
                f.write(p + '\n')

        with open('{}/{}/{}.txt'.format(args.root_dir, sub, 'train'), 'w+') as f:
            for p in img_path[:len(img_path) - int(len(img_path)*0.1)]:
                f.write(p + '\n')

        with open('{}/{}/{}.txt'.format(args.root_dir, sub, 'val'), 'w+') as f:
            for p in img_path[len(img_path) - int(len(img_path)*0.1):len(img_path) - int(len(img_path)*0.05)]:
                f.write(p + '\n')
        
        with open('{}/{}/{}.txt'.format(args.root_dir, sub, 'test'), 'w+') as f:
            for p in img_path[len(img_path) - int(len(img_path)*0.05):]:
                f.write(p + '\n')

def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='/home/husan/lightvision/datasets')
    parser.add_argument('--sub_dir', action='append', type=str,
                        help='list of target VOC datasets')
    parser.add_argument('--img_ext', type=str,
                        help='extension of image files', default='jpg')
    

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
