import pytest

from tracker.vehicle_lifecycle import VehicleLifecycle


def test_car_seen_in_every_frame():
    lifecycle = VehicleLifecycle(max_missing_frames=3)
    track_id = 1
    for i in range(1,11):
        lifecycle.mark_seen_vehicle(track_id)
        expired_ids = lifecycle.frame_end()
        assert expired_ids == []


def test_car_returns_before_expiration():
    lifecycle = VehicleLifecycle(max_missing_frames=3)
    track_id = 1

    lifecycle.mark_seen_vehicle(track_id)
    assert lifecycle.frame_end() == []

    for _ in range(2):
        assert lifecycle.frame_end() == []

    lifecycle.mark_seen_vehicle(track_id)
    assert lifecycle.frame_end() == []

    for _ in range(2):
        assert lifecycle.frame_end() == []


def test_car_expire_at_limit():
    lifecycle = VehicleLifecycle(max_missing_frames=3)
    track_id = 1
    lifecycle.mark_seen_vehicle(track_id)
    assert lifecycle.frame_end() == []
    for _ in range (2):
        assert lifecycle.frame_end() == []

    assert lifecycle.frame_end() == [track_id]


def test_expired_car_is_returned_only_once():
    lifecycle = VehicleLifecycle(max_missing_frames=3)
    track_id = 1
    lifecycle.mark_seen_vehicle(track_id)
    assert lifecycle.frame_end() == []

    for _ in range (2):
        assert lifecycle.frame_end() == []

    assert lifecycle.frame_end() == [track_id]

    for _ in range (2):
        assert lifecycle.frame_end() == []
    

def test_only_missing_vehicle_expires():
    lifecycle = VehicleLifecycle(max_missing_frames=3)
    first_track_id = 1
    second_track_id = 2

    lifecycle.mark_seen_vehicle(first_track_id)
    lifecycle.mark_seen_vehicle(second_track_id)
    assert lifecycle.frame_end() == []

    for _ in range(2):
        lifecycle.mark_seen_vehicle(first_track_id)
        assert lifecycle.frame_end() == []

    lifecycle.mark_seen_vehicle(first_track_id)
    assert lifecycle.frame_end() == [second_track_id]

    lifecycle.mark_seen_vehicle(first_track_id)
    assert lifecycle.frame_end() == []


def test_readable_frame_counter_resets_after_expiration():
    lifecycle = VehicleLifecycle(max_missing_frames=3)
    track_id = 1

    for _ in range(5):
        lifecycle.mark_seen_vehicle(track_id)
        readable_frames = lifecycle.increment_readable_frame(track_id)
        lifecycle.frame_end()

    assert readable_frames == 5

    for _ in range (2):
        assert lifecycle.frame_end() == []


    assert lifecycle.frame_end() == [track_id]
    lifecycle.mark_seen_vehicle(track_id)
    assert lifecycle.increment_readable_frame(track_id) == 1


def test_vehicle_expiration_at_tracker_boundary():
    lifecycle = VehicleLifecycle(max_missing_frames=13)
    track_id = 1
    lifecycle.mark_seen_vehicle(track_id)
    lifecycle.frame_end()

    for _ in range(1,13):
        assert lifecycle.frame_end() == []

    assert lifecycle.frame_end() == [track_id]
    assert lifecycle.frame_end() == []


def test_increment_readable_frame_unknown_id():
    lifecycle = VehicleLifecycle(max_missing_frames=3)
    track_id = 1

    with pytest.raises(ValueError):
        lifecycle.increment_readable_frame(track_id)

@pytest.mark.parametrize("max_missing_frames", [0, -1, -10])
def test_invalid_max_missing_frames(max_missing_frames):
    with pytest.raises(ValueError):

        VehicleLifecycle(max_missing_frames)

def test_frame_end_without_vehicles():
    lifecycle = VehicleLifecycle(max_missing_frames=3)
    assert lifecycle.frame_end() == []