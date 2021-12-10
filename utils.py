import os
import glob
from typing import KeysView
import cv2
import json
import sys
import numpy as np
from pathlib import Path
from shutil import move, copy
from xml.etree import cElementTree as ElementTree

class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})

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
            raise Exception("file exists!", "Can't copy to")
        else:
            copy(src, dst)
            print('file has been copied to "{}/"'.format(dst))

    except IOError as e:
        print('unable to copy file %s' % e)
        bool_success = False

    except Exception as e:
        print('{} {} "{}/"'.format(e.args[0], e.args[1], os.path.join(dst)))
        bool_success = False
    except:
        print('unexpected error:', sys.exc_info())
        bool_success = False
    finally:
        return bool_success


def get_box_x(path, filename, file_ext):
    labels = []
    box_list = []
    file_path = '{}/{}{}'.format(path, filename, file_ext)    
    tree = ElementTree.parse(file_path)            
    root = tree.getroot()
    h = 0.0
    w = 0.0
               
    for size in root.findall('size'):          
        
        h = float(size.find('height').text)
        w = float(size.find('width').text)

    for obj in root.findall('object'):          
        labels.append(obj.find('name').text)
        # h = distros_dict['imageHeight']
        # w = distros_dict['imageWidth']
        
        c = obj.find('name').text
        b1 = obj.find('bndbox').find('xmin').text
        b2 = obj.find('bndbox').find('xmax').text
        b3 = obj.find('bndbox').find('ymin').text
        b4 = obj.find('bndbox').find('ymax').text
        b = (float(b1), float(b2), float(b3), float(b4))
        
        box_list.append([c, w, h, b[0], b[1], b[2], b[3]])
    return box_list
    

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

def get_box_taco(path, filename):

    with open('{}/{}.json'.format(path, filename), 'r') as f:
        distros_dict = json.load(f)
    print('INFO: ', distros_dict['info'])    
    images = distros_dict['images']
    annotations = distros_dict['annotations']    
    taco_list = []
    for image in images:                
        # print(images[i])
        # print(annotations[i])
        
        
        # annotation = annotations[i]
        # print(image['id'])
        
        # print(image['width'])
        # print(image['height'])
        # print(image['file_name'])
        file_name = image['file_name']
        w = image['width']
        h = image['height']
        box_list = []
        for annotation in annotations:            
            if annotation['image_id'] == image['id']:
                # print(annotation['id'])
                # print(annotation['category_id'])
                # print(annotation['bbox'])
                c = str(annotation['category_id'])
                xmlbox = annotation['bbox']

                    

                b = (float(xmlbox[0]), float(xmlbox[0] + xmlbox[2]), float(xmlbox[1]), float(xmlbox[1] + xmlbox[3]))
                bb = convert((w, h), b)

                # print('{:f} {:f} {:f} {:f}\n'.format(bb[0], bb[1], bb[2], bb[3]))
                # out_file.write('{:f} {:f} {:f} {:f}\n'.format(bb[0], bb[1], bb[2], bb[3]))
                box_list.append([c, w, h, b[0], b[1], b[2], b[3]])

        taco_list.append([file_name, box_list])

    # h = distros_dict['imageHeight']
    # w = distros_dict['imageWidth']


    # for obj in distros_dict['shapes']:
    #     c = obj['label']
    #     # print(c)
    #     # label = c.partition("_")[0][:-2]  # nplate
    #     # label_index = c.partition("_")[0] # nplate10
    #     # print(label, label_index)

    #     if c is None:
    #         continue

    #     xmlbox = obj['points']

    #     b = (float(xmlbox[0][0]), float(xmlbox[1][0]), float(
    #         xmlbox[0][1]), float(xmlbox[1][1]))
    #     bb = convert((w, h), b)

    #     # print('{:f} {:f} {:f} {:f}\n'.format(bb[0], bb[1], bb[2], bb[3]))
    #     # out_file.write('{:f} {:f} {:f} {:f}\n'.format(bb[0], bb[1], bb[2], bb[3]))
    #     box_list.append([c, w, h, b[0], b[1], b[2], b[3]])

    return taco_list

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

def check_json_parameters(path, filename, modified_dir = 'modified_json'):
    wrong_annotation = False
    json_dict = {}
    if True:
    # try:        
        with open('{}/{}.json'.format(path, filename), 'r') as f:
            distros_dict = json.load(f)
            
            

        h = distros_dict['imageHeight']
        w = distros_dict['imageWidth']
        shapes = []

        for obj in distros_dict['shapes']:                       
            
            xmlbox = obj['points']
            
            
            x0 = float(xmlbox[0][0]) 
            x1 = float(xmlbox[1][0]) 
            y0 = float(xmlbox[0][1]) 
            y1 = float(xmlbox[1][1])

            if x0 < 0:
                x0 = 0
                wrong_annotation = True

            if x1 < 0: 
                x1 = 0
                wrong_annotation = True

            if y0 < 0:
                y0 = 0
                wrong_annotation = True

            if y1 < 0:
                y1 = 0
                wrong_annotation = True
                

            if x0 > w:
                x0 = w
                wrong_annotation = True

            if x1 > w:
                x1 = w
                wrong_annotation = True

            if y0 > h:
                y0 = h
                wrong_annotation = True

            if y1 > h:
                y1 = h
                wrong_annotation = True            

            if x0 > x1:                
                x = x0
                x0 = x1
                x1 = x
                wrong_annotation = True

            if y0 > y1:                
                y = y0
                y0 = y1
                y1 = y
                wrong_annotation = True
                
            obj['points'] = [[x0, y0],[x1, y1]]            
            shapes.append(obj)
        
        if wrong_annotation:
            json_dict = distros_dict        
            json_dict['shapes'] = shapes        
            with open('{}/{}/{}.json'.format(path,modified_dir, filename), 'w') as out_file:
                out_file.write(json.dumps(json_dict,ensure_ascii=False, indent=4))

    # except IOError as e:
    #     # print('IOError: %s' % e)
    #     labels = []
    # except Exception as e:
    #     # print('{} {} '.format(e.args[0], e.args[1]))
    #     labels = []
    # except:
    #     # print('unexpected error:', sys.exc_info())
    #     labels = []
    # finally:
    #     return labels

    

    return True
    


def get_lables_x(path, filename, file_ext):
    labels = []
    file_path = '{}/{}{}'.format(path, filename, file_ext)
    try:
    # if True:
        distros_dict = {}
        if file_ext == '.json':
            with open(file_path, 'r') as f:
                distros_dict = json.load(f)
        if file_ext == '.xml':
            tree = ElementTree.parse(file_path)            
            root = tree.getroot()
            # distros_dict = XmlDictConfig(root)
           
        # for obj in distros_dict['annotation']:
        for obj in root.findall('object'):          
            labels.append(obj.find('name').text)


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


def get_lables(path, filename, file_ext):
    labels = []
    file_path = '{}/{}{}'.format(path, filename, file_ext)
    try:
    # if True:
        distros_dict = {}
        if file_ext == '.json':
            with open(file_path, 'r') as f:
                distros_dict = json.load(f)
        if file_ext == '.xml':
            tree = ElementTree.parse(file_path)
            root = tree.getroot()
            distros_dict = XmlDictConfig(root)
        
        h = distros_dict['imageHeight']
        w = distros_dict['imageWidth']

        for obj in distros_dict['shapes']:
            xmlbox = obj['points']
            b = (float(xmlbox[0][0]), float(xmlbox[1][0]), float(xmlbox[0][1]), float(xmlbox[1][1]))

            if b[0] < 0 or b[1] < 0 or b[2] < 0 or b[3] < 0:
                raise Exception("wrong annotation")
            print(b[0] , b[1] , w , b[2] , b[3] , h)
            if b[0] > w or b[1] > w or b[2] > h or b[3] > h:
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


def cut_label_x(path, filename, box_list, img_folder = 'images', crop_img_folder = 'cropped_images', margin = 0.0):
    success = False
    # c, w, h, x0, x1, y0,
    # try:
    if True:
        crop_img_folder = Path(os.path.join(path, crop_img_folder))
        print('crop_folder:', crop_img_folder)
        crop_img_folder.mkdir(parents=True, exist_ok=True)
        image_path = os.path.join('{}/{}/{}'.format(path, img_folder, filename))
        print('Reading file {}'.format(image_path))
        img = cv2.imread(image_path)
        img.shape

        label_count = 0

        for c, w, h, x0, x1, y0, y1 in box_list:
            print(c, w, h, x0, x1, y0, y1)
            crop_img_c_folder = Path(os.path.join(crop_img_folder, c))
            print(crop_img_c_folder)
            crop_img_c_folder.mkdir(parents=True, exist_ok=True)

            label_count += 1


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
            print(crop_img.shape)
            crop_img_path = os.path.join('{}/{}_{}_{}.jpg'.format(crop_img_c_folder, filename[:-4], '{0:003}'.format(label_count), c))
            print(crop_img_path)

            cv2.imwrite(crop_img_path, crop_img)
            cv2.waitKey(0)

        success = True
    # except AttributeError:
    #     print("file does not have shape")
    #     success = False
    # finally:
        print(label_count)
        return success


def cut_label_taco(path, filename, box_list, crop_img_folder = 'cropped_images', margin = 0.0):
    success = False
    # c, w, h, x0, x1, y0,
    # try:
    if True:
        crop_img_folder = Path(os.path.join(path, crop_img_folder))
        print('crop_folder:', crop_img_folder)
        crop_img_folder.mkdir(parents=True, exist_ok=True)
        image_path = os.path.join('{}/{}'.format(path, filename))
        print('Reading file {}'.format(image_path))
        img = cv2.imread(image_path)
        img.shape

        label_count = 0

        for c, w, h, x0, x1, y0, y1 in box_list:
            print(c, w, h, x0, x1, y0, y1)
            crop_img_c_folder = Path(os.path.join(crop_img_folder, c))
            print(crop_img_c_folder)
            crop_img_c_folder.mkdir(parents=True, exist_ok=True)

            label_count += 1


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
            print(crop_img.shape)
            
            crop_img_path = os.path.join('{}/{}_{}_{}.jpg'.format(crop_img_c_folder, filename[:-4].split('/')[-1], '{0:003}'.format(label_count), c))
            print(crop_img_path)

            cv2.imwrite(crop_img_path, crop_img)
            cv2.waitKey(0)

        success = True
    # except AttributeError:
    #     print("file does not have shape")
    #     success = False
    # finally:
        print(label_count)
        return success

def cut_label_genome(path, filename, box_list, crop_img_folder = 'cropped_images', margin = 0.0):
    success = False
    # c, w, h, x0, x1, y0,
    # try:
    if True:
        crop_img_folder = Path(os.path.join(path, crop_img_folder))
        print('crop_folder:', crop_img_folder)
        crop_img_folder.mkdir(parents=True, exist_ok=True)
        image_path = os.path.join('{}/{}'.format(path, filename))
        print('Reading file {}'.format(image_path))
        img = cv2.imread(image_path)
        img.shape

        label_count = 0

        for c, w, h, x0, x1, y0, y1 in box_list:
            print(c, w, h, x0, x1, y0, y1)
            crop_img_c_folder = Path(os.path.join(crop_img_folder, c))
            print(crop_img_c_folder)
            crop_img_c_folder.mkdir(parents=True, exist_ok=True)

            label_count += 1


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
            print(crop_img.shape)
            
            crop_img_path = os.path.join('{}/{}_{}_{}.jpg'.format(crop_img_c_folder, filename[:-4].split('/')[-1], '{0:003}'.format(label_count), c))
            print(crop_img_path)

            cv2.imwrite(crop_img_path, crop_img)
            cv2.waitKey(0)

        success = True
    # except AttributeError:
    #     print("file does not have shape")
    #     success = False
    # finally:
        print(label_count)
        return success


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
        # c = c.partition("_")[0][:-2] # nplate

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

def convert_annotation_taco(path, filename, classes):

    with open('{}/Annotations/{}.json'.format(path, filename), 'r') as f:
        distros_dict = json.load(f)
    print('INFO: ', distros_dict['info'])    
    images = distros_dict['images']
    annotations = distros_dict['annotations']    
        # print(annotation)
    
    for i in range(len(images)):
        print()
        # print(images[i])
        # print(annotations[i])
        
        image = images[i]
        annotation = annotations[i]
        print(image['id'])
        print(image['width'])
        print(image['height'])
        print(image['file_name'])

        print(annotation['id'])
        print('image_id: ', annotation['image_id'])
        print(annotation['category_id'])
        print(annotation['bbox'])
        
    
    
    
    
    # h = distros_dict['imageHeight']
    # w = distros_dict['imageWidth']

    # for obj in distros_dict['shapes']:
    #     c = obj['label']
    #     # c = c.partition("_")[0] # nplate10
    #     # c = c.partition("_")[0][:-2] # nplate

    #     if c not in classes == 1:
    #         continue

    #     cid = classes.index(c)

    #     print('class_name:', c, ',', cid)

    #     xmlbox = obj['points']

    #     b = (float(xmlbox[0][0]), float(xmlbox[1][0]), float(
    #         xmlbox[0][1]), float(xmlbox[1][1]))
    #     bb = convert((w, h), b)

    #     out_file = open(
    #         '{}/JPEGImages/{}.txt'.format(path, filename), 'a+')
    #     print('file name:','{}/JPEGImages/{}.txt'.format(path, filename))
    #     out_file.write('{} {:f} {:f} {:f} {:f}\n'.format(
    #         cid, bb[0], bb[1], bb[2], bb[3]))

def convert_annotation_x(path, filename, classes):    
    
    file_path = '{}/Annotations/{}.xml'.format(path, filename)
    tree = ElementTree.parse(file_path)            
    root = tree.getroot()
    h = 0.0
    w = 0.0

    for size in root.findall('size'):                  
        h = float(size.find('height').text)
        w = float(size.find('width').text)

    for obj in root.findall('object'): 
        c = obj.find('name').text        
        if c not in classes == 1:
            continue

        cid = classes.index(c)

        # print('class_name:', c, ',', cid)

        b1 = obj.find('bndbox').find('xmin').text
        b2 = obj.find('bndbox').find('xmax').text
        b3 = obj.find('bndbox').find('ymin').text
        b4 = obj.find('bndbox').find('ymax').text
        b = (float(b1), float(b2), float(b3), float(b4))
        bb = convert((w, h), b)

        out_file = open(
            '{}/labels/{}.txt'.format(path, filename), 'a+')
        # print('file name:','{}/labels/{}.txt'.format(path, filename))
        out_file.write('{} {:f} {:f} {:f} {:f}\n'.format(
            cid, bb[0], bb[1], bb[2], bb[3]))
