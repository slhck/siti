#!/usr/bin/env python3
import numpy as np
import av
import sys
import skvideo.io

input_file = sys.argv[1]

container = av.open(input_file)

for packet in container.demux():
    for frame in packet.decode():
        if isinstance(frame, av.video.frame.VideoFrame):
            frame_data_raw = np.frombuffer(frame.planes[0], np.uint8)
            print(np.mean(frame_data_raw))

for frame in skvideo.io.vreader(sys.argv[1], as_grey=True):
    width = frame.shape[-2]
    height = frame.shape[-3]
    frame_data_raw = frame.reshape((height, width))
    print(np.mean(frame_data_raw))
    break