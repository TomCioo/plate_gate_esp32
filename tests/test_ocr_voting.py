import pytest

from ocr.ocr_voting import OcrVoting


@pytest.fixture
def voting():
    return OcrVoting(0.6, 6, 20)


def test_too_few_readings(voting):
    for _ in range(5):
        voting.add_reading(1, "KRA12345")

    assert voting.get_confirmed_plate(1) is None


def test_clear_winner(voting):
    for _ in range(6):
        voting.add_reading(1, "KRA12345")

    for _ in range(2):
        voting.add_reading(1, "KNT123456")

    assert voting.get_confirmed_plate(1) == "KRA12345"


def test_no_clear_winner(voting):
    plates = ["KRA12345"] * 3 + ["KNT123456"] * 3 + ["KWA12345"] * 2

    for plate in plates:
        voting.add_reading(1, plate)

    assert voting.get_confirmed_plate(1) is None


def test_forget_confirmed_plate(voting):
    for _ in range(6):
        voting.add_reading(1, "KRA12345")

    assert voting.get_confirmed_plate(1) == "KRA12345"

    voting.forget_track(1)

    assert voting.get_confirmed_plate(1) is None


def test_forget_unknown_track(voting):
    voting.forget_track(2)

    assert voting.get_confirmed_plate(2) is None


def test_ignore_empty_readings(voting):
    for plate in [None, "", "", "", "", "", None]:
        voting.add_reading(1, plate)

    assert voting.get_confirmed_plate(1) is None


def test_history_limit():
    voting = OcrVoting(0.6, 1, 3)

    for plate in ["KRA11111", "KRA22222", "KRA33333", "KRA44444"]:
        voting.add_reading(1, plate)

    assert len(voting.history[1]) == 3
    assert "KRA11111" not in voting.history[1]


def test_forget_one_track_keeps_another():
    voting = OcrVoting(0.6, 2, 20)

    for _ in range(2):
        voting.add_reading(1, "KRA12345")
        voting.add_reading(2, "KNT12345")

    voting.forget_track(1)

    assert voting.get_confirmed_plate(1) is None
    assert voting.get_confirmed_plate(2) == "KNT12345"


def test_exactly_min_ratio():
    voting = OcrVoting(0.6, 5, 20)

    for plate in ["KRA12345"] * 3 + ["KNT12345"] * 2:
        voting.add_reading(1, plate)

    assert voting.get_confirmed_plate(1) == "KRA12345"


def test_below_min_ratio():
    voting = OcrVoting(0.6, 5, 20)

    for plate in ["KRA12345"] * 4 + ["KNT12345"] * 3:
        voting.add_reading(1, plate)

    assert voting.get_confirmed_plate(1) is None


@pytest.mark.parametrize(
    "min_reads, history_size",
    [
        (0, 20),
        (10, 5),
    ],
)
def test_invalid_min_reads(min_reads, history_size):
    with pytest.raises(ValueError):
        OcrVoting(0.6, min_reads, history_size)


@pytest.mark.parametrize(
    "min_ratio",
    [0, 0.5, 1.5],
)
def test_invalid_min_ratio(min_ratio):
    with pytest.raises(ValueError):
        OcrVoting(min_ratio, 6, 20)
