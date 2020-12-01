import os
import glob
import cv2
import json
import sys
from pathlib import Path
from shutil import move
def remove_annot_files(path):
    annot_list = glob.glob(os.path.join(path, 'JPEGImages/*.txt'))
    for annot in annot_list:
        try:
            os.remove(annot)
        except:
            print('unable to delete: ' + annot)



def move_file_to_directories(path, src_folder, dis_folder, file_name, overwrite=False):
    dis_path = Path(os.path.join(path, dis_folder))
    dis_path.mkdir(exist_ok=True)
    src_path = Path(os.path.join(path, src_folder))
    try:
        if os.path.exists(os.path.join(dis_path, file_name)) and not overwrite:
            raise Exception("file exists!", "Can't move to")
        else:
            move(os.path.join(src_path, file_name), os.path.join(dis_path, file_name))
            print('file has been moved to "{}/"'.format(dis_path))

    except IOError as e:
        print('unable to move file %s' % e)
        exit(1)
    except Exception as e:
        print('{} {} "{}/"'.format(e.args[0], e.args[1], os.path.join(path, p)))
    except:
        print('unexpected error:', sys.exc_info())
        exit(1)






