#!/usr/bin/env python3

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import siti.__main__ as siti

import numpy as np
import pytest

input_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "test.mp4"))

ground_truth = os.path.abspath(os.path.join(os.path.dirname(__file__), "siti.csv"))


def read_gt(what="si"):
    ret = {
        "si": [],
        "ti": []
    }
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
def si_gt():
    si_gt = read_gt(what="si")
    return si_gt


@pytest.fixture
def ti_gt():
    ti_gt = read_gt(what="ti")
    return ti_gt


def test_avg_si(si, si_gt):
    print(np.mean(si))
    print(np.mean(si_gt))
    assert round(np.mean(si), 2) == round(np.mean(si_gt), 2)


def test_avg_ti(ti, ti_gt):
    assert round(np.mean(ti), 2) == round(np.mean(ti_gt), 2)


def main():
    si, ti, num_frames = siti.calculate_si_ti(input_file, quiet=True)
    si_gt = read_gt("si")
    ti_gt = read_gt("ti")
    print([round(x, 2) for x in si])
    print([round(x, 2) for x in si_gt])
    print([round(x, 2) for x in ti])
    print([round(x, 2) for x in ti_gt])
    print(num_frames)


if __name__ == "__main__":
    main()
