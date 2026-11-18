import pytest
import numpy as np

from main import crop_plate

def test_valid_plate_crop():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    assert crop_plate(20,40,30,50,5,frame).shape == (30,30,3)


def test_plate_crop_at_edge():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    assert crop_plate(2, 20, 3, 15, 10, frame).shape == (25,30,3)