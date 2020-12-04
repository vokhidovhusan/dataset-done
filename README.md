# dataset-done

### installations

#### pip
```
$ wget https://bootstrap.pypa.io/get-pip.py
$ sudo python3 get-pip.py
```
#### OpenCV
```$ pip install opencv-contrib-python```
#### Python labraries
```$ pip install scipy matplotlib pillow```
#### Tensorflow and Keras

```
$ pip install tensorflow
$ pip install keras
```

### Run
#### extract images from multiple videos
Extracts every frame by default from multiple videos and saves the extracted images in a folder.

```python extract-images-from-video.py multiple_videos --dir [videos_path]```

for example:
```ython extract-images-from-video.py multiple_videos --dir  video/```

You want to assign nth number so that you can take ever nth frame from a video.

```python extract-images-from-video.py multiple_videos --dir [video_path] --n_frames [integer number]```

For examples

```python extract-images-from-video.py multiple_videos --dir  video/ --n_frame 20```

#### extract images from single video

Extracts images from single video and saves the extracted images in a folder.

```python extract-images-from-video.py single_video --path [video_path]```

for example:
```python extract-images-from-video.py single_video --path video/videoplayback.mp4```

To assign nth number.

```python extract-images-from-video.py single_video --path [video_path] --n_frames [integer number]```

For examples

```python extract-images-from-video.py single_video --path video/videoplayback.mp4 --n_frame 20```