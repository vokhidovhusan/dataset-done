import argparse
import os
import sys
import cv2
from pathlib import Path

def save_image(image_path, image_name, image, overwrite=False):
    try:
        if os.path.exists(os.path.join(image_path, image_name)) and not overwrite:
            raise Exception("file exists!", "Can't create a frame")
        else:
            cv2.imwrite(os.path.join(image_path, image_name), image)
            print('a frame has been created')
    except IOError as e:
        print('unable to crate a frame %s' % e)
        exit(1)
    except Exception as e:
        print('{} {} "{}/"'.format(e.args[0], e.args[1], os.path.join(image_path, image_name)))
    except:
        print('unexpected error:', sys.exc_info())
        exit(1)



def main(args):
    with os.scandir(args.video_path) as entries:
        for entry in entries:
            if entry.is_file():
                # Read image
                print('Reading video file {}'.format(entry.name))
                try:
                    image_path = Path(os.path.join('{}_frames'.format(entry.path)))
                    image_path.mkdir(exist_ok=True)
                except OSError as e:
                    print(e)

                # try:
                if True:
                    vidcap = cv2.VideoCapture(entry.path)
                    # success, image = vidcap.read()
                    count = 0
                    # success = True
                    while vidcap.isOpened():
                        ret, image = vidcap.read()
                        if not ret:
                            break
                        print('read a new frame:')
                        if count % args.n_frames == 0:
                            image_name = "{}_frame_{}.jpg".format(entry.name,'{0:000000009}'.format(count))
                            save_image(image_path, image_name, image)
                        count += 1
                    vidcap.release()
    cv2.destroyAllWindows()


def parse_arguments(argv):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--video_path", type=str, default='video', help="videos for extracting")
    parser.add_argument('--n_frames', type=int, default=5, help='number for captureing every nth from a video')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
