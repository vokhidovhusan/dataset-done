from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Dict
import os

class XMLHandler:
    def __init__(self, xml_path: str or Path):
        self.xml_path = Path(xml_path)
        self.root = self.__open()

    def __open(self):
        with self.xml_path.open() as opened_xml_file:
            self.tree = ET.parse(opened_xml_file)
            return self.tree.getroot()

    def return_boxes_class_as_dict(self) -> Dict[int, Dict]:
        boxes_dict = {}
        for index, sg_box in enumerate(self.root.iter('object')):
            boxes_dict[index] = {"name": sg_box.find("name").text,
                                 "xmin": int(sg_box.find("bndbox").find("xmin").text),
                                 "ymin": int(sg_box.find("bndbox").find("ymin").text),
                                 "xmax": int(sg_box.find("bndbox").find("xmax").text),
                                 "ymax": int(sg_box.find("bndbox").find("ymax").text)}

        return boxes_dict


def converter(xml_files: str, output_folder: str) -> None:
    xml_files = [file for file in os.listdir('../datasets/SEOULSUL_TEST_DATA/json_to_voc') if file.endswith('.xml')]

    for xml_index, xml in enumerate(xml_files):
        print(xml)
        file_name = xml[:-4]
        filename = "{}.txt".format(file_name)
        
        filename_path = Path(output_folder) / filename
        xml_content = XMLHandler('../datasets/SEOULSUL_TEST_DATA/json_to_voc/'+xml)
        boxes = xml_content.return_boxes_class_as_dict()

        with open(filename_path, "a") as file:
            for box_index in boxes:
                box = boxes[box_index]
                if box['name']=='-':
                    continue
                print(box['name'])
                box_content = f"{box['name']} {box['xmin']} {box['ymin']} {box['xmax']} {box['ymax']}\n"
                file.write(box_content)

    print(f"Converted {len(xml_files)} files!")

    
if __name__ == '__main__':
    XML_FOLDER = "../datasets/SEOULSUL_TEST_DATA/json_to_voc/"
    OUTPUT_FOLDER =  "../datasets/SEOULSUL_TEST_DATA/icdar"
    if not os.path.exists('../datasets/SEOULSUL_TEST_DATA/icdar/'):
        os.mkdir('../datasets/SEOULSUL_TEST_DATA/icdar/')
    converter(XML_FOLDER, OUTPUT_FOLDER)