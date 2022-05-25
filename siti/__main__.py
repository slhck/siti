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
from enum import Enum
from typing import Generator, Optional
import av
import json
import numpy as np
import os
import sys
from tqdm import tqdm
from scipy import ndimage

from .__init__ import __version__ as version


def si(frame_data: np.ndarray) -> float:
    """Calculate SI of a frame

    Args:
        frame_data (ndarray): 2D array of input frame data

    Returns:
        float: SI
    """
    # TODO: check array dimensions

    # calculate horizontal/vertical operators
    sob_x = ndimage.sobel(frame_data, axis=0)
    sob_y = ndimage.sobel(frame_data, axis=1)

    # crop output to valid window, calculate gradient magnitude
    si = np.hypot(sob_x, sob_y)[1:-1, 1:-1].std()
    return si


def ti(
    frame_data: np.ndarray, previous_frame_data: Optional[np.ndarray]
) -> Optional[float]:
    """
    Calculate TI between two frames.

    Args:
        frame_data (ndarray): 2D array of current frame data
        previous_frame_data (ndarray): 2D array of previous frame data, must be of same size as current frame

    Returns:
        float: TI, or None if previous frame data is not given
    """
    # TODO: check array dimensions
    # TODO: check array dimensions equal between both args

    if previous_frame_data is None:
        return None
    else:
        return (frame_data - previous_frame_data).std()


class FileFormat(Enum):
    YUV420P = 1


def _convert_range(y_data: np.ndarray) -> np.ndarray:
    # check if we don't actually exceed minimum range
    if np.min(y_data) < 16 or np.max(y_data) > 235:
        raise RuntimeError(
            "Input YUV appears to be full range, specify full_range=True!"
        )
    # convert to grey by assumng limited range input
    y_data = np.around((y_data - 16) / ((235 - 16) / 255))
    return y_data


def read_yuv(
    input_file: str,
    width: int,
    height: int,
    file_format=FileFormat.YUV420P,
    full_range=False,
) -> Generator[np.ndarray, None, None]:
    """Read a YUV420p file and yield the per-frame Y data

    Args:
        input_file (str): Input file path
        width (int): Width in pixels
        height (int): Height in pixels
        file_format (str, optional): The input file format. Defaults to FileFormat.YUV420P.
        full_range (bool, optional): Whether to assume full range input. Defaults to False.

    Raises:
        NotImplementedError: If a wrong file format is chosen

    Yields:
        np.ndarray: The frame data, integer
    """
    # TODO: add support for other YUV types
    if file_format != FileFormat.YUV420P:
        raise NotImplementedError("Other file formats are not yet implemented!")

    # get the number of frames
    file_size = os.path.getsize(input_file)

    num_frames = file_size // (width * height * 3 // 2)

    with open(input_file, "rb") as in_f:
        for _ in range(num_frames):
            y_data = (
                np.frombuffer(in_f.read((width * height)), dtype=np.uint8)
                .reshape((height, width))
                .astype("int")
            )

            # read U and V components, but skip
            in_f.read((width // 2) * (height // 2) * 2)

            # in case we need the data later, you can uncomment this:
            # u_data = (
            #     np.frombuffer(in_f.read(((width // 2) * (height // 2))), dtype=np.uint8)
            #     .reshape((height // 2, width // 2))
            #     .astype("int")
            # )
            # v_data = (
            #     np.frombuffer(in_f.read(((width // 2) * (height // 2))), dtype=np.uint8)
            #     .reshape((height // 2, width // 2))
            #     .astype("int")
            # )

            if not full_range:
                # check if we don't actually exceed minimum range
                y_data = _convert_range(y_data)

            yield y_data


def read_container(
    input_file: str, full_range=False
) -> Generator[np.ndarray, None, None]:
    """Read a multiplexed file via ffmpeg and yield the per-frame Y data

    Args:
        input_file (str): Input file path

    Raises:
        RuntimeError: If no video streams were found

    Yields:
        np.ndarray: The frame data, integer
    """
    container = av.open(input_file)

    if not len(container.streams.video):
        raise RuntimeError("No video streams found!")

    for frame in container.decode(video=0):
        frame_data = (
            frame.to_ndarray(format="gray")
            .reshape(frame.height, frame.width)
            .astype("int")
        )

        if not full_range:
            # check if we don't actually exceed minimum range
            frame_data = _convert_range(frame_data)
        yield frame_data


def get_num_frames(input_file: str, width=None, height=None):
    """
    Use PyAV or simple math to get the number of frames in a container
    """
    if input_file.endswith(".yuv"):
        file_size = os.path.getsize(input_file)
        # FIXME: this is only valid for YUV420
        num_frames = file_size // (width * height * 3 // 2)
    else:
        container = av.open(input_file)
        num_frames = container.streams.video[0].frames
        if num_frames == 0:
            num_frames = None
            print(
                "Warning: frame count could not be detected from stream",
                file=sys.stderr,
            )
    return num_frames


def calculate_si_ti(
    input_file: str, quiet=False, num_frames=0, width=0, height=0, full_range=False
):
    """
    Calculate SI and TI from an input file

    Arguments:
        input_file {str} -- path to input file

    Keyword Arguments:
        quiet {bool} -- do not output tqdm progress bar (default: {False})
        num_frames {int} -- number of frames to parse (default: {0})
        width {int} -- frame width for YUV files (default: None)
        height {int} -- frame height for YUV files (default: None)
        full_range {bool} –- assume full range for YUV files (default: False)

    Returns:
        - [si_values], [ti_values], frame count
    """
    si_values = []
    ti_values = [0.0]
    previous_frame_data = None

    if input_file.endswith(".yuv"):
        print(
            "Warning: Reading YUV files may produce values different from what "
            "you would get if you analyzed a muxed (e.g. MP4) file.. "
            "See https://github.com/slhck/siti/issues/4 for more info.",
            file=sys.stderr,
        )
        kwargs = {
            "width": width,
            "height": height,
            "full_range": full_range,
            "file_format": FileFormat.YUV420P,
        }
        iterator_fun = read_yuv
    else:
        kwargs = {
            "full_range": full_range,
        }
        iterator_fun = read_container

    # if the user didn't specify a maximum, get it from the container
    if num_frames == 0:
        num_frames = get_num_frames(input_file, width=width, height=height)

    t = tqdm(total=num_frames, disable=quiet, file=sys.stderr)

    current_frame = 0
    for frame_data in iterator_fun(input_file, **kwargs):
        # print(f"  [{np.around(np.min(frame_data), 3)}, {np.around(np.max(frame_data), 3)}], mean {np.around(np.mean(frame_data), 3)}, median {np.around(np.median(frame_data), 3)}")
        si_value = si(frame_data)
        si_values.append(si_value)

        ti_value = ti(frame_data, previous_frame_data)
        if ti_value is not None:
            ti_values.append(ti_value)

        previous_frame_data = frame_data

        current_frame += 1
        t.update()
        if num_frames is not None and current_frame >= num_frames:
            return si_values, ti_values, current_frame

    t.close()
    return si_values, ti_values, current_frame


def main():
    parser = argparse.ArgumentParser(
        prog="siti", description="siti v{}".format(version), formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("input", help="input file", type=str)
    parser.add_argument(
        "-of",
        "--output-format",
        type=str,
        choices=["json", "csv"],
        default="json",
        help="output format",
    )
    parser.add_argument(
        "-q", "--quiet", help="do not show progress bar", action="store_true"
    )
    parser.add_argument(
        "-n",
        "--num-frames",
        help="number of frames to calculate, must be >= 2",
        type=int,
    )
    parser.add_argument("--width", help="frame width (for YUV files)", type=int)
    parser.add_argument("--height", help="frame height (for YUV files)", type=int)
    parser.add_argument(
        "-f",
        "--full-range",
        help="assume full range for YUV input",
        action="store_true",
    )
    cli_args = parser.parse_args()

    if (cli_args.num_frames is not None) and cli_args.num_frames < 2:
        print("Need at least -n 2!", file=sys.stderr)
        sys.exit(1)

    if cli_args.input.endswith(".yuv") and not (cli_args.width and cli_args.height):
        print("Need to specify --width and --height for YUV!", file=sys.stderr)
        sys.exit(1)

    si_orig, ti_orig, num_frames = calculate_si_ti(
        cli_args.input,
        quiet=cli_args.quiet,
        num_frames=cli_args.num_frames,
        width=cli_args.width,
        height=cli_args.height,
        full_range=cli_args.full_range,
    )

    si_list = np.round(np.array(si_orig).astype(float), 3).tolist()
    ti_list = np.round(np.array(ti_orig).astype(float), 3).tolist()

    if cli_args.output_format == "json":
        data = {
            "input_file": os.path.abspath(cli_args.input),
            "si": si_list,
            "ti": ti_list,
            "avg_si": round(np.mean(si_list), 3),
            "avg_ti": round(np.mean(ti_list[1:]), 3),
            "max_si": round(np.max(si_list), 3),
            "min_si": round(np.min(si_list), 3),
            "max_ti": round(np.max(ti_list[1:]), 3),
            "min_ti": round(np.min(ti_list[1:]), 3),
            "std_si": round(np.std(si_list), 3),
            "std_ti": round(np.std(ti_list[1:]), 3),
            "num_frames": num_frames,
        }
        data_dump = json.dumps(data, indent=True, sort_keys=True)

        print(data_dump)

    elif cli_args.output_format == "csv":
        import csv

        writer = csv.writer(sys.stdout)

        data = {
            "input_file": [os.path.abspath(cli_args.input)] * num_frames,
            "si": si_list,
            "ti": ti_list,
            "n": range(1, num_frames + 1),
        }

        writer.writerow(data.keys())
        writer.writerows(zip(*data.values()))

    else:
        raise RuntimeError("Wrong output format")


if __name__ == "__main__":
    main()
