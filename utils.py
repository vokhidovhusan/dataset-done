import os
import glob
import cv2
import json
import sys
import numpy as np
from pathlib import Path
from shutil import move, copy


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


def copy_file_to_directories_full_path(src, dst,  overwrite=False):
    bool_success = True
    try:
        if os.path.exists(dst) and not overwrite:
            raise Exception("file exists!", "Can't move to")
        else:
            copy(src, dst)
            print('file has been copied to "{}/"'.format(dst))

    except IOError as e:
        print('unable to move file %s' % e)
        bool_success = False

    except Exception as e:
        print('{} {} "{}/"'.format(e.args[0], e.args[1], os.path.join(dst)))
        bool_success = False
    except:
        print('unexpected error:', sys.exc_info())
        bool_success = False
    finally:
        return bool_success

def get_box(path, filename):

    with open('{}/{}.json'.format(path, filename), 'r') as f:
        distros_dict = json.load(f)

    h = distros_dict['imageHeight']
    w = distros_dict['imageWidth']

    box_list = []

    for obj in distros_dict['shapes']:
        c = obj['label']
        # print(c)
        # label = c.partition("_")[0][:-2]  # nplate
        # label_index = c.partition("_")[0] # nplate10
        # print(label, label_index)

        if c is None:
            continue

        xmlbox = obj['points']

        b = (float(xmlbox[0][0]), float(xmlbox[1][0]), float(
            xmlbox[0][1]), float(xmlbox[1][1]))
        bb = convert((w, h), b)

        # print('{:f} {:f} {:f} {:f}\n'.format(bb[0], bb[1], bb[2], bb[3]))
        # out_file.write('{:f} {:f} {:f} {:f}\n'.format(bb[0], bb[1], bb[2], bb[3]))
        box_list.append([c, w, h, b[0], b[1], b[2], b[3]])


    cv2.destroyAllWindows()
    return box_list

def get_json_parameters(path, filename):

    with open('{}/{}.json'.format(path, filename), 'r') as f:
        distros_dict = json.load(f)

    h = distros_dict['imageHeight']
    w = distros_dict['imageWidth']
    
    box_list = []

    for obj in distros_dict['shapes']:
        c = obj['label']
        # print(c)
        # label = c.partition("_")[0][:-2]  # nplate
        # label_index = c.partition("_")[0] # nplate10
        # print(label, label_index)

        if c is None:
            continue

        xmlbox = obj['points']

        # print('{:f} {:f} {:f} {:f}\n'.format(bb[0], bb[1], bb[2], bb[3]))
        # out_file.write('{:f} {:f} {:f} {:f}\n'.format(bb[0], bb[1], bb[2], bb[3]))
        box_list.append([c, xmlbox])

    box_list = sorted(box_list, key=lambda x: x[1][0][0], reverse=False)
    # cv2.destroyAllWindows()
    return box_list, [h, w]

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

def resizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


def cut_label(path, filename, box_list, img_folder = 'images', crop_img_folder = 'cropped_images', margin = 0.1):
    success = False
    # c, w, h, x0, x1, y0,
    try:
        crop_img_folder = Path(os.path.join(path, crop_img_folder))
        print(crop_img_folder)
        crop_img_folder.mkdir(parents=True, exist_ok=True)
        image_path = os.path.join('{}/{}/{}.jpg'.format(path, img_folder, filename))
        print('Reading file {}'.format(image_path))
        img = cv2.imread(image_path)
        img.shape

        label_count = 0

        for c, w, h, x0, x1, y0, y1 in box_list:

            crop_img_c_folder = Path(os.path.join(crop_img_folder, c))
            print(crop_img_c_folder)
            crop_img_c_folder.mkdir(parents=True, exist_ok=True)

            label_count += 1
            print(c, w, h, x0, x1, y0, y1)


            margin_y = (y1 - y0) * margin 
            print(margin_y)
            margin_x = (x1 - x0) * margin
            print(margin_x)

            if y0 - margin_y > 0:
                yy0 = y0 - margin_y 
            else:
                yy0 = 0

            if y1 + margin_y < h:
                yy1 = y1 + margin_y
            else:
                yy1 = h

            if x0 - margin_x > 0:
                xx0 = x0 - margin_x
            else:
                xx0 = 0

            if x1 + margin_x < w:
                xx1 = x1 + margin_x
            else:
                xx1 = w
            print(w, h, x0, x1, y0, y1)
            crop_img = img[int(yy0):int(yy1), int(xx0):int(xx1)]

            print('{}/{}_{}_{}.jpg'.format(crop_img_c_folder, filename, '{0:003}'.format(label_count), c))
            crop_img_path = os.path.join('{}/{}_{}_{}.jpg'.format(crop_img_c_folder, filename, '{0:003}'.format(label_count), c))

            cv2.imwrite(crop_img_path, crop_img)
            cv2.waitKey(0)

        success = True
    except AttributeError:
        print("file does not have shape")
        success = False
    finally:
        return success

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



