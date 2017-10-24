#!/usr/bin/env python3
#
# Author: Werner Robitza <werner.robitza@gmail.com>
#
# Calculate SI / TI from input file.
#
# Requirements:
# - scipy
# - numpy
# - av
# - tqdm
#
# Outputs SI/TI statistics as JSON to stderr or to a file.
#
# siti, Copyright (c) 2017 Werner Robitza
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import av
import json
import numpy as np
import os
from scipy import ndimage
import sys
from tqdm import tqdm


def calculate_si(frame_data, magnitude=False):
    """
    Calculate SI of a frame.

    Arguments:
        - frame_data {ndarray}

    Keyword Arguments:
        - magnitude {bool} -- whether to use the magnitude-based calculation

    Returns:
        - {float}
    """
    if not magnitude:
        # P.910 description:
        si = ndimage.sobel(frame_data).std()
    else:
        # Other implementation based on magnitude:
        dx = ndimage.sobel(frame_data, 1)  # horizontal derivative
        dy = ndimage.sobel(frame_data, 0)  # vertical derivative
        mag = np.hypot(dx, dy)  # magnitude
        mag = np.array(mag, dtype=np.uint8)
        si = mag.std()
    return si


def calculate_ti(frame_data, previous_frame_data):
    """
    Calculate TI between two frames.

    Arguments:
        frame_data {ndarray} -- current frame
        previous_frame_data {ndarray} -- previous frame, must be of same size as current frame

    Returns:
        - {float}
    """
    if previous_frame_data is None:
        return None
    else:
        return (frame_data - previous_frame_data).std()


def calculate_si_ti(input_file, quiet=False, num_frames=0, magnitude=False):
    """
    Calculate SI and TI from an input file

    Arguments:
        input_file {str} -- path to input file

    Keyword Arguments:
        quiet {bool} -- do not output tqdm progress bar (default: {False})
        num_frames {int} -- number of frames to parse (default: {0})
        magnitude {bool} -- use alternative calculation for SI magnitude (default: {False})

    Returns:
        - [si_values], [ti_values], frame count
    """
    si_values = []
    ti_values = []

    container = av.open(input_file)

    previous_frame_data = None

    # initialize progress
    if not num_frames:
        num_frames = container.streams.video[0].frames
    t = tqdm(total=num_frames, disable=quiet)

    frame_index = 0
    for packet in container.demux():
        for frame in packet.decode():
            if isinstance(frame, av.video.frame.VideoFrame):
                frame_data = np.frombuffer(frame.planes[0], np.uint8).reshape(frame.height, frame.width)

                si = calculate_si(frame_data, magnitude)
                si_values.append(si)

                ti = calculate_ti(frame_data, previous_frame_data)
                if ti is not None:
                    ti_values.append(ti)

                previous_frame_data = frame_data

                frame_index += 1
                t.update()
                if frame_index >= num_frames:
                    return si_values, ti_values, frame_index

    t.close()
    return si_values, ti_values, frame_index


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        help="input file"
    )
    parser.add_argument(
        "-o", "--output",
        help="output JSON file"
    )
    parser.add_argument(
        "-q", "--quiet",
        help="do not show progress bar",
        action="store_true"
    )
    parser.add_argument(
        "-n", "--num-frames",
        help="number of frames to calculate",
        type=int
    )
    parser.add_argument(
        "-m", "--magnitude",
        help="use magnitude-based way to calculate SI",
        action="store_true"
    )
    cli_args = parser.parse_args()

    if (cli_args.num_frames is not None) and cli_args.num_frames < 2:
        print("Need at least -n 2!", file=sys.stderr)
        sys.exit(1)

    si, ti, num_frames = calculate_si_ti(
        cli_args.input,
        quiet=cli_args.quiet,
        num_frames=cli_args.num_frames,
        magnitude=cli_args.magnitude
    )

    data = {
        "filename": os.path.abspath(cli_args.input),
        "SI": si,
        "TI": ti,
        "avgSI": np.mean(si),
        "avgTI": np.mean(ti),
        "maxSI": np.max(si),
        "minSI": np.min(si),
        "maxTI": np.max(ti),
        "minTI": np.min(ti),
        "stdSI": np.std(si),
        "stdTI": np.std(ti),
        "numFrames": num_frames,
    }

    if cli_args.output:
        with open(cli_args.output, "w") as of:
            json.dump(data, of, indent=True, sort_keys=True)
    else:
        print(json.dumps(data, indent=True, sort_keys=True))


if __name__ == '__main__':
    main()
