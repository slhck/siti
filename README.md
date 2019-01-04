# SITI: Spatial Information / Temporal Information

A command-line-based tool to calculate spatial information (SI) and temporal information (TI) according to ITU-T P.910.

The command outputs SI and TI information to stdout, in JSON format. If the `-o` option is given, output will be redirected to a file instead.

**Note:** As there are no test vectors for SI / TI implementations, and filter calculations differ depending on how you implement them, the values obtained with this tool may not be comparable with output from other tools.

## Requirements

- Python 3 with
  - numpy
  - scipy
  - av
  - tqdm
- FFmpeg libraries

You can install these with:

    pip3 install --user av tqdm scipy numpy

And (under Ubuntu):

    sudo apt install libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libavfilter-dev libswscale-dev libavresample-dev

## Installation

Clone this repository and then:

    pip3 install --user .
    siti /path/to/input.mp4

Alternatively, run:

    python3 -m siti /path/to/input.mp4

## Usage

    usage: siti [-h] [-o OUTPUT] [-q] [-n NUM_FRAMES] [-m] input

    positional arguments:
      input                 input file

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT, --output OUTPUT
                            output JSON file
      -q, --quiet           do not show progress bar
      -n NUM_FRAMES, --num-frames NUM_FRAMES
                            number of frames to calculate
      -m, --magnitude       use magnitude-based way to calculate SI

## Background

The following info is given about SI / TI in ITU-T Recommendation P.910 ("Subjective video quality assessment methods for multimedia applications"):

### Spatial Information

> The spatial perceptual information (SI) is based on the Sobel filter. Each video frame (luminance plane) at time n (Fn) is first filtered with the Sobel filter [Sobel(Fn)]. The standard deviation over the pixels (stdspace) in each Sobel-filtered frame is then computed. This operation is repeated for each frame in the video sequence and results in a time series of spatial information of the scene. The maximum value in the time series (maxtime) is chosen to represent the spatial information content of the scene. This process can be represented in equation form as:

> ![](http://i.imgur.com/zRXcVJO.png)

### Temporal information

> The temporal perceptual information (TI) is based upon the motion difference feature, Mn(i, j), which is the difference between the pixel values (of the luminance plane) at the same location in space but at successive times or frames. Mn(i, j) as a function of time (n) is defined as:

> ![](http://i.imgur.com/MRsJtdT.png)

> here Fn(i, j) is the pixel at the ith row and jth column of nth frame in time.
The measure of temporal information (TI) is computed as the maximum over time (maxtime) of the standard deviation over space (stdspace) of Mn(i, j) over all i and j.

> <img src="https://i.imgur.com/XAnKWJw.png" height="19">

> More motion in adjacent frames will result in higher values of TI

## License

siti, Copyright (c) 2017, 2018 Werner Robitza

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
