import json
import os
from pascal_voc_writer import Writer
import cv2

json_list=[file for file in os.listdir('../datasets/SEOULSUL_TEST_DATA/Annotations/') if file.endswith('.json')]
print(len(json_list))
if not os.path.exists('../datasets/SEOULSUL_TEST_DATA/json_to_voc'):
    os.makedirs('../datasets/SEOULSUL_TEST_DATA/json_to_voc')

for i in json_list:
    img_name=i[:-5]+'.jpg'
    img_path='../datasets/SEOULSUL_TEST_DATA/JPEGImages/'+img_name
    xml_name=i[:-5]+'.xml'
    img=cv2.imread(img_path)
    height, width, channels = img.shape
    writer= Writer(img_path,width,height)
    with open('../datasets/SEOULSUL_TEST_DATA/Annotations/'+i) as json_file:
        json_list=json.load(json_file)['shapes']
        for data in json_list:
            label=data['label']
            label=label.split('_')
            label=label[1]
            cords=data['points']
            xmin,ymin,xmax,ymax=int(cords[0][0]),int(cords[0][1]),int(cords[1][0]),int(cords[1][1])
            writer.addObject(label,xmin,ymin,xmax,ymax)
    writer.save('../datasets/SEOULSUL_TEST_DATA/json_to_voc/'+xml_name)