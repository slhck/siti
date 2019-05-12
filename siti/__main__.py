#!/usr/bin/env python3
#
# Author: Werner Robitza <werner.robitza@gmail.com>
#
# Calculate SI / TI from input file.
#
# Requirements:
# - scipy
# - numpy
# - pyav
# - tqdm
#
# Outputs SI/TI statistics as JSON to stderr or to a file.

import argparse
import av
import json
import numpy as np
import os
from scipy import ndimage
import sys
from tqdm import tqdm

from .__init__ import __version__ as version


def calculate_si(frame_data):
    """
    Calculate SI of a frame.

    Arguments:
        - frame_data {ndarray}

    Keyword Arguments:
        - magnitude {bool} -- whether to use the magnitude-based calculation

    Returns:
        - {float}
    """
    sob_x = ndimage.sobel(frame_data, axis=0)
    sob_y = ndimage.sobel(frame_data, axis=1)
    si = np.hypot(sob_x, sob_y).std()
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


def calculate_si_ti(input_file, quiet=False, num_frames=0):
    """
    Calculate SI and TI from an input file

    Arguments:
        input_file {str} -- path to input file

    Keyword Arguments:
        quiet {bool} -- do not output tqdm progress bar (default: {False})
        num_frames {int} -- number of frames to parse (default: {0})
        magnitude {bool} -- use alternative calculation for SI magnitude (default: {True})

    Returns:
        - [si_values], [ti_values], frame count
    """
    si_values = []
    ti_values = [0.0]

    container = av.open(input_file)

    previous_frame_data = None

    # get video
    if not len(container.streams.video):
        raise RuntimeError("No video streams found!")

    # initialize progress
    if not num_frames:
        num_frames = container.streams.video[0].frames
        if num_frames == 0:
            num_frames = None
            print("Warning: frame count could not be detected from stream", file=sys.stderr)
    t = tqdm(total=num_frames, disable=quiet, file=sys.stderr)

    current_frame = 0
    for frame in container.decode(video=0):
        frame_data = frame.to_ndarray(format="gray").reshape(frame.height, frame.width).astype("float32")

        si = calculate_si(frame_data)
        si_values.append(si)

        ti = calculate_ti(frame_data, previous_frame_data)
        if ti is not None:
            ti_values.append(ti)

        previous_frame_data = frame_data

        current_frame += 1
        t.update()
        if num_frames is not None and current_frame >= num_frames:
            return si_values, ti_values, current_frame

    t.close()
    return si_values, ti_values, current_frame


def main():
    parser = argparse.ArgumentParser(prog="siti", description="siti v{}".format(version))
    parser.add_argument(
        "input",
        help="input file"
    )
    parser.add_argument(
        "-of", "--output-format",
        type=str,
        choices=["json", "csv"],
        default="json",
        help="output format"
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
    cli_args = parser.parse_args()

    if (cli_args.num_frames is not None) and cli_args.num_frames < 2:
        print("Need at least -n 2!", file=sys.stderr)
        sys.exit(1)

    si_orig, ti_orig, num_frames = calculate_si_ti(
        cli_args.input,
        quiet=cli_args.quiet,
        num_frames=cli_args.num_frames
    )

    si = np.round(np.array(si_orig).astype(float), 3).tolist()
    ti = np.round(np.array(ti_orig).astype(float), 3).tolist()

    if cli_args.output_format == "json":
        data = {
            "input_file": os.path.abspath(cli_args.input),
            "si": si,
            "ti": ti,
            "avg_si": round(np.mean(si), 3),
            "avg_ti": round(np.mean(ti), 3),
            "max_si": round(np.max(si), 3),
            "min_si": round(np.min(si), 3),
            "max_ti": round(np.max(ti), 3),
            "min_ti": round(np.min(ti), 3),
            "std_si": round(np.std(si), 3),
            "std_ti": round(np.std(ti), 3),
            "num_frames": num_frames,
        }
        data_dump = json.dumps(data, indent=True, sort_keys=True)

        print(data_dump)

    elif cli_args.output_format == "csv":
        import csv

        writer = csv.writer(sys.stdout)

        data = {
            "input_file": [os.path.abspath(cli_args.input)] * num_frames,
            "si": si,
            "ti": ti,
            "n": range(1, num_frames + 1)
        }

        writer.writerow(data.keys())
        writer.writerows(zip(*data.values()))

    else:
        raise RuntimeError("Wrong output format")


if __name__ == '__main__':
    main()
