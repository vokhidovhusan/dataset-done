import os
import glob
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


def convert(size, box):
    dw = 1.0 / (size[0])
    dh = 1.0 / (size[1])
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def remove_label_json_files(path):
    annot_list = glob.glob(os.path.join(path, '*.json'))
    for annot in annot_list:
        try:
            os.remove(annot)
        except:
            print('unable to delete: ' + annot)


def move_file_to_directories(path, dis_folder, file_name, overwrite=False):
    bool_success = True
    p = Path(os.path.join(path, dis_folder))
    p.mkdir(exist_ok=True)
    try:
        if os.path.exists(os.path.join(p, file_name)) and not overwrite:
            raise Exception("file exists!", "Can't move to")
        else:
            move(os.path.join(path, file_name), os.path.join(p, file_name))
            print('file has been moved to "{}/"'.format(os.path.join(path, p)))

    except IOError as e:
        print('unable to move file %s' % e)
        bool_success = False

    except Exception as e:
        print('{} {} "{}/"'.format(e.args[0], e.args[1], os.path.join(path, p)))
        bool_success = False
    except:
        print('unexpected error:', sys.exc_info())
        bool_success = False
    finally:
        return bool_success




def get_lables(path, filename):
    labels = []
    try:
        with open('{}/{}.json'.format(path, filename), 'r') as f:
            distros_dict = json.load(f)

        h = distros_dict['imageHeight']
        w = distros_dict['imageWidth']

        for obj in distros_dict['shapes']:
            xmlbox = obj['points']
            b = (float(xmlbox[0][0]), float(xmlbox[1][0]), float(xmlbox[0][1]), float(xmlbox[1][1]))

            if b[0] < 0 or b[1] < 0 or b[2] < 0 or b[3] < 0:
                raise Exception("wrong annotation")

            if b[0] >= b[1]:
                labels = []
                raise Exception("wrong annotation")
            if b[2] >= b[3]:
                labels = []
                raise Exception("wrong annotation")

            c = obj['label']
            # c = c.partition("_")[0] # nplate10
            # c = c.partition("_")[0][:-2] # nplate
            labels.append(c)

    except IOError as e:
        # print('IOError: %s' % e)
        labels = []
    except Exception as e:
        # print('{} {} '.format(e.args[0], e.args[1]))
        labels = []
    except:
        # print('unexpected error:', sys.exc_info())
        labels = []
    finally:
        return labels




def convert_annotation(path, filename, classes):

    with open('{}/Annotations/{}.json'.format(path, filename), 'r') as f:
        distros_dict = json.load(f)

    h = distros_dict['imageHeight']
    w = distros_dict['imageWidth']

    for obj in distros_dict['shapes']:
        c = obj['label']
        # c = c.partition("_")[0] # nplate10
        c = c.partition("_")[0][:-2] # nplate

        if c not in classes == 1:
            continue

        cid = classes.index(c)

        print('class_name:', c, ',', cid)

        xmlbox = obj['points']

        b = (float(xmlbox[0][0]), float(xmlbox[1][0]), float(
            xmlbox[0][1]), float(xmlbox[1][1]))
        bb = convert((w, h), b)

        out_file = open(
            '{}/JPEGImages/{}.txt'.format(path, filename), 'a+')
        print('file name:','{}/JPEGImages/{}.txt'.format(path, filename))
        out_file.write('{} {:f} {:f} {:f} {:f}\n'.format(
            cid, bb[0], bb[1], bb[2], bb[3]))



