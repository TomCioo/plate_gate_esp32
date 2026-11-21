import numpy as np

from frame_utils import crop_plate


def test_valid_plate_crop():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    bbox = (40, 30, 40, 50)

    assert crop_plate(bbox, 5, frame).shape == (30, 10, 3)


def test_plate_crop_at_edge():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    bbox = (2, 3, 20, 15)

    assert crop_plate(bbox, 10, frame).shape == (25, 30, 3)


def test_plate_crop_at_bottom_right_edge():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    bbox = (85, 80, 98, 97)

    assert crop_plate(bbox, 10, frame).shape == (30, 25, 3)