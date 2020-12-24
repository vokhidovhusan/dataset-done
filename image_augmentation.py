#Importing class
import os
import sys
from random import randrange
import numpy as np
import argparse
from pathlib import Path
from numpy import expand_dims
import cv2
import utils





def increase_brightness(img, value=10):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img


def noisy(noise_typ,image):
    if noise_typ == "gauss":
        row,col,ch= image.shape
        mean = 0
        var = 0.1
        sigma = var**0.5
        gauss = np.random.normal(mean,sigma,(row,col,ch))
        gauss = gauss.reshape(row,col,ch)
        noisy = image + gauss
        return noisy
    elif noise_typ == "s&p":
        row,col,ch = image.shape
        s_vs_p = 0.5
        amount = 0.004
        out = np.copy(image)
        # Salt mode
        num_salt = np.ceil(amount * image.size * s_vs_p)
        coords = [np.random.randint(0, i - 1, int(num_salt))for i in image.shape]
        out[coords] = 1
        # Pepper mode
        num_pepper = np.ceil(amount* image.size * (1. - s_vs_p))
        coords = [np.random.randint(0, i - 1, int(num_pepper))for i in image.shape]
        out[coords] = 0
        return out
    elif noise_typ == "poisson":
        vals = len(np.unique(image))
        vals = 2 ** np.ceil(np.log2(vals))
        noisy = np.random.poisson(image * vals) / float(vals)
        return noisy
    elif noise_typ =="speckle":
        row,col,ch = image.shape
        gauss = np.random.randn(row,col,ch)
        gauss = gauss.reshape(row,col,ch)        
        noisy = image + image * gauss
        return noisy
    

def blur(src):
    dst = cv2.GaussianBlur(src,(3,3),cv2.BORDER_DEFAULT)
    return dst


def contrast(img):
    alpha = 1.5 # Contrast control (1.0-3.0)
    beta = 0 # Brightness control (0-100)

    adjusted = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    return adjusted


def motion_horizontal_blur(img):
    size = randrange(1, 3)
    # generating the horizontal kernel
    kernel_motion_blur = np.zeros((size, size))
    kernel_motion_blur[int((size-1)/2), :] = np.ones(size)
    kernel_motion_blur = kernel_motion_blur / size

    # applying the kernel to the input image
    output = cv2.filter2D(img, -1, kernel_motion_blur)
    return output


def motion_vertical_blur(img):
    size = randrange(1, 5)
    kernel_motion_blur = np.zeros((size, size))
    kernel_motion_blur[:int((size-1)/2),] = np.ones(size)
    kernel_motion_blur = kernel_motion_blur / size
    # applying the kernel to the input image
    output = cv2.filter2D(img, -1, kernel_motion_blur)
    return output


def run_aug_data_generatorimage(entry, AUGMENTED_IMAGES):
    from keras.preprocessing.image import load_img
    from keras.preprocessing.image import img_to_array
    from keras.preprocessing.image import ImageDataGenerator
    from keras.preprocessing.image import ImageDataGenerator
    #Creating instance of the ImageDataGenerator class
    datagen = ImageDataGenerator(
            rotation_range=10,
            width_shift_range=0.1,
            height_shift_range=0.1,
            rescale=1./255,
            shear_range=0.5,
            zoom_range=0.1,
            horizontal_flip=True,
            brightness_range=[0.5,1.0], 
            fill_mode='nearest'
            )

    try:
        # load the image
        img=cv2.imread(entry.path)
        
        
        # converting to numpy array
        data = img_to_array(img)
        
        # expanding the dimension to one sample
        samples = expand_dims(data, 0)

        # creating image data augmentation generator
        datagen = ImageDataGenerator(
            rotation_range=5, 
            #horizontal_flip=0, 
            brightness_range = [0.5,1.0], 
            width_shift_range=0.1, 
            height_shift_range=0.1,
            zoom_range=0.1
        )

        # preparing iterator
        it = datagen.flow(samples, batch_size=1)
        
        cv2.imwrite('{}/{}_aug_org.jpg'.format(AUGMENTED_IMAGES, file,), img, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        # generating samples and plotting
        for i in range(2):
            # generating batch of images
            batch = it.next()
            # converting to unsigned integers for viewing
            image = batch[0].astype('uint8')
            cv2.imwrite('{}/{}_aug_{}.jpg'.format(AUGMENTED_IMAGES, file, i), image,[int(cv2.IMWRITE_JPEG_QUALITY), 100])
    
    except OSError as e:
        print(e)
    
    except:
        print('An exception occurred')


def main(args):
    run_blur= args.blur
    brightness = args.brightness
    noise = args.noise
    contrast_ratio = args.contrast_ratio
    motion_blur_hori= args.motion_blur_hori
    data_generator = False        

    root = args.root
    JPEGImages = os.path.join('{}/{}'.format(root, args.images))
    LABELS = os.path.join('{}/{}'.format(root, args.labels))
    
    AUGMENTED_IMAGES = Path(os.path.join('{}/augmented_{}'.format(root, args.images)))
    AUGMENTED_IMAGES.mkdir(exist_ok=True)
    AUGMENTED_LABELS = Path(os.path.join('{}/augmented_{}'.format(root, args.labels)))
    AUGMENTED_LABELS.mkdir(exist_ok=True)
    count = 0
    for image_path, dirs, files  in os.walk(JPEGImages):
        
        for file in files:
            if file.endswith('.jpg'):
                try:
                    file_name = os.path.splitext(file)[0]                
                    print(file_name)

                    # Read image                    
                    img=cv2.imread('{}/{}'.format(image_path, file))                    
                    img.shape
                                                                
                    utils.copy_file_to_directories_full_path('{}/{}.jpg'.format(JPEGImages, file_name), '{}/{}.jpg'.format(AUGMENTED_IMAGES, count))
                    utils.copy_file_to_directories_full_path('{}/{}.txt'.format(LABELS, file_name), '{}/{}.txt'.format(AUGMENTED_LABELS, count))

                    if run_blur:
                        index = 'blur'
                        blur_img = blur(img)                        
                        cv2.imwrite('{}/{}_{}.jpg'.format(AUGMENTED_IMAGES, count, index), blur_img)                                                
                        utils.copy_file_to_directories_full_path('{}/{}.txt'.format(LABELS, file_name), '{}/{}_{}.txt'.format(AUGMENTED_LABELS, count, index))
                    if brightness:
                        index = 'brightness'
                        img_brightness = increase_brightness(img)
                        cv2.imwrite('{}/{}_{}.jpg'.format(AUGMENTED_IMAGES, count, index), img_brightness)                        
                        utils.copy_file_to_directories_full_path('{}/{}.txt'.format(LABELS, file_name), '{}/{}_{}.txt'.format(AUGMENTED_LABELS, count, index))
                    if noise:
                        index = 'noise'
                        noi = ['s&p','gauss','gauss']
                        n = np.random.choice(noi,1,replace = False)
                        img_noise = noisy(n, img)
                        cv2.imwrite('{}/{}_{}.jpg'.format(AUGMENTED_IMAGES, count, index), img_noise)                        
                        utils.copy_file_to_directories_full_path('{}/{}.txt'.format(LABELS, file_name), '{}/{}_{}.txt'.format(AUGMENTED_LABELS, count, index))
                    if contrast_ratio:
                        index = 'contrast'
                        contrast_img = contrast(img)
                        cv2.imwrite('{}/{}_{}.jpg'.format(AUGMENTED_IMAGES, count, index), contrast_img)                                          
                        utils.copy_file_to_directories_full_path('{}/{}.txt'.format(LABELS, file_name), '{}/{}_{}.txt'.format(AUGMENTED_LABELS, count, index))  
                    if motion_blur_hori:
                        index = 'motion'
                        motion_img = motion_horizontal_blur(img)
                        cv2.imwrite('{}/{}_{}.jpg'.format(AUGMENTED_IMAGES, count, index), motion_img)
                        utils.copy_file_to_directories_full_path('{}/{}.txt'.format(LABELS, file_name), '{}/{}_{}.txt'.format(AUGMENTED_LABELS, count, index))
                    count += 1        
                except OSError as e:
                    print(e)
    


def parse_arguments(argv):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--root", required=True, 
                        help="your dataset root directory for augmentation", 
                        type=str,)    
    parser.add_argument("--images", default='images', 
                        help="image directory for augmentation", 
                        type=str,)
    parser.add_argument("--labels", default='labels', 
                        help="label directory for augmentation", 
                        type=str,)
    parser.add_argument('--blur',
                        action='store_false',
                        help='enable brightness')
    parser.add_argument('--brightness',
                        action='store_false',
                        help='enable brightness')
    parser.add_argument('--noise',
                        action='store_false',
                        help='enable noise')
    parser.add_argument('--contrast_ratio',
                        action='store_false',
                        help='enable contrast ratio')
    parser.add_argument('--motion_blur_hori',
                        action='store_false',
                        help='enable horizontal motion blur')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
