#!/usr/bin/env python3

import sys
import os
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import siti.__main__ as siti

import numpy as np
import pytest

input_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "test.mp4"))

ground_truth = os.path.abspath(os.path.join(os.path.dirname(__file__), "siti.csv"))


def read_gt(what="si"):
    ret = {"si": [], "ti": []}
    with open(ground_truth, "r") as gtf:
        header_read = False
        for line in gtf.readlines():
            if not header_read:
                header_read = True
                continue
            line = line.strip()
            si, ti, _ = line.split(",")
            ret["si"].append(float(si))
            ret["ti"].append(float(ti))
    return ret[what]


@pytest.fixture
def si():
    si, _, _ = siti.calculate_si_ti(input_file, quiet=True)
    return si


@pytest.fixture
def ti():
    _, ti, _ = siti.calculate_si_ti(input_file, quiet=True)
    return ti


@pytest.fixture
def si_yuv(yuv_file):
    si, _, _ = siti.calculate_si_ti(yuv_file, width=320, height=240, quiet=True)
    return si


@pytest.fixture
def ti_yuv(yuv_file):
    _, ti, _ = siti.calculate_si_ti(yuv_file, width=320, height=240, quiet=True)
    return ti


@pytest.fixture
def si_gt():
    si_gt = read_gt(what="si")
    return si_gt


@pytest.fixture
def ti_gt():
    ti_gt = read_gt(what="ti")
    return ti_gt


@pytest.fixture
def yuv_file():
    yuv_file_path = input_file.replace(".mp4", ".yuv")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_file,
        "-c:v",
        "rawvideo",
        "-f",
        "rawvideo",
        yuv_file_path,
    ]
    subprocess.check_output(cmd)
    yield yuv_file_path
    if os.path.isfile(yuv_file_path):
        os.remove(yuv_file_path)


def test_avg_si(si, si_gt):
    assert abs(np.mean(si) - np.mean(si_gt)) < 0.01


def test_avg_ti(ti, ti_gt):
    assert abs(np.mean(ti) - np.mean(ti_gt)) < 0.01


def test_avg_si_yuv(si_yuv, si_gt):
    assert abs(np.mean(si_yuv) - np.mean(si_gt)) < 1


def test_avg_ti_yuv(ti_yuv, ti_gt):
    assert abs(np.mean(ti_yuv) - np.mean(ti_gt)) < 0.05


# def main():
#     si, ti, num_frames = siti.calculate_si_ti(input_file, quiet=True)
#     si_gt = read_gt("si")
#     ti_gt = read_gt("ti")
#     print([round(x, 2) for x in si])
#     print([round(x, 2) for x in si_gt])
#     print([round(x, 2) for x in ti])
#     print([round(x, 2) for x in ti_gt])
#     print(num_frames)
