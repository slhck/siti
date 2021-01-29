# SITI: Spatial Information / Temporal Information

[![PyPI version](https://badge.fury.io/py/siti.svg)](https://badge.fury.io/py/siti)

A command-line-based tool to calculate spatial information (SI) and temporal information (TI) according to ITU-T P.910.

The command outputs SI and TI information to stdout, in JSON format, or alternatively as CSV.

Author: Werner Robitza

**Important Note / Breaking Changes:**

* Version 1.3 fixes an issue with border handling, now returning values that should better match ITU-T Rec. P.910. Thanks to Cosmin Stejerean for raising these issues.
* Version 1.x now outputs the same number of values for SI and TI, inserting a null value for the first frame's TI. Also, the output format has been changed.
* Version 0.x produces incorrect values due to wrong reading of the data using PyAV. Version 1.x and above produces correct values in the sense of corresponding to [this implementation](https://github.com/Telecommunication-Telemedia-Assessment/SITI/). As there are no test vectors for SI / TI implementations, and filter calculations differ depending on how you implement them, the values obtained with this tool may not be comparable with output from other tools.

Contents:

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Background](#background)
- [License](#license)

## Requirements

- Python 3
- FFmpeg libraries (to run `pyav`)

Under Ubuntu, to get ffmpeg libraries:

    sudo apt install libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libavfilter-dev libswscale-dev libavresample-dev

Under macOS, it is recommended to install ffmpeg via [Homebrew](https://brew.sh):

    brew install ffmpeg

## Installation

Run:

    pip3 install --user siti

Alternatively, clone this repository and then:

    pip3 install --user .

## Usage

Simply run `siti /path/to/file.mp4`.

Detailed usage:

```
siti [-h] [-of {json,csv}] [-q] [-n NUM_FRAMES] [--width WIDTH] [--height HEIGHT] input

positional arguments:
  input                 input file

optional arguments:
  -h, --help            show this help message and exit
  -of {json,csv}, --output-format {json,csv}
                        output format
  -q, --quiet           do not show progress bar
  -n NUM_FRAMES, --num-frames NUM_FRAMES
                        number of frames to calculate
  --width WIDTH         frame width (for YUV files)
  --height HEIGHT       frame height (for YUV files)
  -f, --full-range      assume full range for YUV input
```

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

siti, Copyright (c) 2017-2019 Werner Robitza

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
