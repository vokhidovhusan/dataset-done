import os
import sys
import argparse
import json
import cv2
from numpy.lib.type_check import imag
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
                    
                    json_dict = {
                            
                            "version": "4.5.6", 
                            "flags": {},                            
                            "imageData": None,                          
                            }

                    print()
                    print(file)
                    box_list, h_w = utils.get_json_parameters(os.path.join(path, 'Annotations'), filename)
                    
                    print(h_w)
                    new_w = h_w[0]*0.5625
                    print('new_w:', new_w)
                    new_h = h_w[0]
                    
                    for box in box_list:
                        print(box)
                    start_end_list = []
                    
                    for box in box_list:
                        shapes_dict = {
                            "group_id": None,
                            "shape_type": "rectangle",
                            "flags": {}
                        }

                        add = True
                        for start_end in start_end_list:
                            if box[1][0][0] >= start_end[0] and box[1][1][0] <= start_end[1]:
                                add = False
                        
                        
                        
                        
                        

                        if add:
                            cx = (box[1][1][0] + box[1][0][0])/2                        
                        
                            start_x = cx - new_w/2 
                            end_x = start_x + new_w
                            
                            if start_x < 0:
                                start_x = 0
                                end_x = new_w
                            if end_x > h_w[1]:
                                end_x = h_w[1]
                                start_x = h_w[1] - new_w
                            
                            shapes_dict['label'] = box[0] 
                            shapes_dict['points'] = [
                                [box[1][0][0]-start_x,box[1][0][1]],
                                [box[1][1][0]-start_x, box[1][1][1]]
                                ]
                            start_end_list.append([start_x, end_x, [shapes_dict]])
                        else:

                            st, en, get_last = start_end_list[-1]
                            shapes_dict['label'] = box[0] 
                            shapes_dict['points'] = [
                                [box[1][0][0]-st,box[1][0][1]],
                                [box[1][1][0]-st, box[1][1][1]]
                                ]
                            
                            get_last.append(shapes_dict)
                            start_end_list[-1] = [st,en,get_last]
                            



                        

                        
                    
                    print(start_end_list)       
                    
                    count = 0  
                    image_path = os.path.join(path, 'Annotations', file.replace('.json', '.jpg'))
                    
                    img = cv2.imread(image_path)
                    
                    # img_resize = utils.resizeWithAspectRatio(img, height=1024)
                    # cv2.imshow('image',img_resize)
                    
                    
                    for start, end,  shapes_d in start_end_list:
                        
                        crop_image_path = '{}/{}_{}.jpg'.format(path, filename, count)
                        json_path = '{}/{}_{}.json'.format(path, filename, count)
                        # print(0,h_w[0], int(start_end[0]), int(start_end[1]))
                        # crop = img[0:h_w[0], int(start_end[0]):int(start_end[1])]
                        crop = img[0:h_w[0], int(start):int(end)]
                        # crop_resize = utils.resizeWithAspectRatio(crop, height=1024)
                        # cv2.imshow('crop{}'.format(count),crop_resize)
                        
                        cv2.imwrite(crop_image_path,crop)
                        print(crop_image_path)    
                        
                        json_dict['shapes'] = shapes_d
                        json_dict['imageHeight'] = new_h
                        json_dict['imageWidth'] = int(end - start)
                        json_dict['imagePath'] = '{}_{}.jpg'.format(filename, count)
                        
                        with open(json_path, 'a+') as out_file:                        
                            out_file.write(json.dumps(json_dict,ensure_ascii=False, indent=4))

                        count += 1

                    # cv2.waitKey(0)
                    # cv2.destroyAllWindows()

                    # success = utils.cut_label(path, filename, box_list, 'JPEGImages', '{}_rnplate'.format(sub))
                    # print(success)
                    # count_json += 1
                    # if success:
                    #     utils.move_file_to_directories(path, 'Annotations', 'Annotations_success', file)
                    #     utils.move_file_to_directories(path, 'JPEGImages', 'JPEGImages_success', file.replace('.json', '.jpg'))
                    #     count_img += 1

                    

    # print(count_json)
    # print(count_img)

def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='/home/husan/lightvision/datasets/')
    parser.add_argument('--sub_dir', action='append', type=str, help='root of VOC development kit')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
