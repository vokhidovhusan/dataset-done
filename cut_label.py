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
                if args.file_ext in file:
                    if not file.endswith(('.json', '.xml')):
                        continue
                    # annotation_folder = Path(os.path.join(path, 'Annotation'))
                    # annotation_folder.mkdir(exist_ok=True)
                    #
                    # image_folder = Path(os.path.join(path, 'JPEGImages'))
                    # image_folder.mkdir(exist_ok=True)

                    filename = file.replace(args.file_ext, '')
                    
                    if args.dataset_name == 'taco':
                        if(args.file_ext == '.json'):
                            filename = file.replace('.json', '')
                            taco_list = utils.get_box_taco(os.path.join(path, 'Annotations'), filename)
                            
                            for file_name, box_list in taco_list:
                                print(file_name)                                
                                print(file_name[-4:])
                                success = utils.cut_label_taco(path, file_name, box_list, '{}_cut'.format(sub))
                                # print(success)
                                # count_json += 1
                                
                                if success:
                                #     utils.move_file_to_directories(path, 'Annotations', 'Annotations_success', file)
                                #     utils.move_file_to_directories(path, 'JPEGImages', 'JPEGImages_success', file.replace('.json', '.jpg'))
                                    count_img += 1                                
                                    print(count_img)
                        if(args.file_ext == '.xml'):
                            pass
                        
                        


                    else:
                        if(args.file_ext == '.json'):
                            filename = file.replace('.json', '')
                            box_list = utils.get_box(os.path.join(path, 'Annotations'), filename)                            

                        if(args.file_ext == '.xml'):
                            box_list = utils.get_box_x(os.path.join(path, 'Annotations'), filename, args.file_ext)
                        
                        print(box_list)
                        success = utils.cut_label_x(path, filename+ '.jpg', box_list, 'images', '{}_cut'.format(sub))
                        print(success)
                        count_json += 1
                        if success:
                            # utils.move_file_to_directories(path, 'Annotations', 'Annotations_success', file)
                            # utils.move_file_to_directories(path, 'JPEGImages', 'JPEGImages_success', file.replace('.json', '.jpg'))
                            count_img += 1

def parse_arguments(argv):

    parser = argparse.ArgumentParser()

    parser.add_argument('--root_dir', type=str,
                        help='root of VOC development kit', default='/home/husan/projects/domestic_waste/yolov5-train/datasets/')
    parser.add_argument('--sub_dir', action='append', type=str, help='root of VOC development kit')
    parser.add_argument('--dataset_name', default='coco', type=str, help='dataset name, for example: coco, taco')
    parser.add_argument('--file_ext', type=str,  help='file extension', default='.json')

    return parser.parse_args(argv)


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
