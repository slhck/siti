#!/usr/bin/env python3

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

import siti.__main__ as siti

import numpy as np
import pytest

input_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "test.mp4"))

@pytest.fixture
def si():
    si, _, _ = siti.calculate_si_ti(input_file, quiet=True)
    return si

@pytest.fixture
def ti():
    _, ti, _ = siti.calculate_si_ti(input_file, quiet=True)
    return ti

def test_avg_si(si):
    assert round(np.mean(si), 2) == 33.44

def test_avg_ti(ti):
    assert round(np.mean(ti), 2) == 10.39

def test_num_si_frames(si):
    assert len(si) == 60

def test_num_ti_frames(ti):
    assert len(ti) == 59

def main():
    si, ti, num_frames = siti.calculate_si_ti(input_file, quiet=True)
    print(si)
    print(ti)
    print(num_frames)

if __name__ == '__main__':
    main()
