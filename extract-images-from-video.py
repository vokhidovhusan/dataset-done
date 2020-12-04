import argparse
import os
from posix import GRND_RANDOM
import sys
import cv2
from pathlib import Path


def save_image(image_directory, file_name, image, overwrite=False):
    try:
        if os.path.exists(os.path.join(image_directory, file_name)) and not overwrite:
            raise Exception("file exists!", "Can't create a frame")
        else:
            cv2.imwrite(os.path.join(image_directory, file_name), image)
            print('a frame has been created')
    except IOError as e:
        print('unable to crate a frame %s' % e)
        exit(1)
    except Exception as e:
        print('{} {} "{}/"'.format(e.args[0], e.args[1], os.path.join(image_directory, file_name)))
    except:
        print('unexpected error:', sys.exc_info())
        exit(1)

def extract_images_from_video(video_path, n_frames):
    vidcap = cv2.VideoCapture(video_path)                
    count = 0

    while vidcap.isOpened():
        ret, frame = vidcap.read()
        if not ret:
            break
        # print('read a new frame:')
        if count % n_frames == 0:
            yield frame, count    
        count += 1
    vidcap.release()


def main(args):
    

    if args.command == 'multiple_videos':
        videos_dir = args.dir
        n_frames = args.n_frames
        with os.scandir(videos_dir) as entries:
            for entry in entries:
                if entry.is_file():                
                    # Read video
                    print('Reading video file {}'.format(entry.name))
                    #create a directory for saving extracted images
                    try:
                        image_dir = Path(os.path.join('{}_frames'.format(entry.path)))
                        image_dir.mkdir(exist_ok=True)               
                    
                        for frame, count in extract_images_from_video(entry.path, n_frames):  
                            frame_name = "{}_frame_{}.jpg".format(entry.name,'{0:000000009}'.format(count))
                            save_image(image_dir, frame_name, frame)                         
                    except OSError as e:
                        print(e)
    
    if args.command == 'single_video':
        videos_path = args.path        
        n_frames = args.n_frames
        try:
            if os.path.exists(videos_path):
                image_dir = Path(os.path.join('{}_frames'.format(videos_path)))
                image_dir.mkdir(exist_ok=True)              
                
                for frame, count in extract_images_from_video(videos_path, n_frames):  
                    frame_name = "{}_frame_{}.jpg".format(videos_path.split('/')[-1],'{0:000000009}'.format(count))
                    save_image(image_dir, frame_name, frame)                         
        except OSError as e:
            print(e)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()        
    subparsers = parser.add_subparsers(dest='command')

    multiple_videos = subparsers.add_parser('multiple_videos')
    subparsers.required = True
    multiple_videos.add_argument("--dir", type=str, required=True, help="direcotry where videos stored for extracting")
    multiple_videos.add_argument('--n_frames', type=int, default=1, help='number for capturing every nth from a video')
    # multiple_videos.set_defaults(subparsers='multiple_videos')
    
    single_video = subparsers.add_parser('single_video')
    subparsers.required = True
    single_video.add_argument('--path', type=str, required=True, help='video path for extracting frames')
    single_video.add_argument('--n_frames', type=int, default=1, help='number for capturing every nth from a video')
    # single_video.set_defaults(subparsers='single_video')

    
    

        
    args = parser.parse_args()
    print(args)
    return args


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
