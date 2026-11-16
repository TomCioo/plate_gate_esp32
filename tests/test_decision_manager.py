import pytest

from types import SimpleNamespace

from decision.decision_manager import DecisionManager


@pytest.fixture
def manager():
    return DecisionManager(open_cooldown=10,retry_cooldown=5,whitelist={"KRA12345"},)


@pytest.fixture
def manager_two_plates():
    return DecisionManager(open_cooldown=10,retry_cooldown=5,whitelist={"KRA12345", "KMY12345"},)

@pytest.fixture
def clock(monkeypatch):
    state = SimpleNamespace(now=0.0)

    monkeypatch.setattr(
        "decision.decision_manager.time.monotonic",
        lambda: state.now,
    )

    return state


def test_try_open_gate_whitelisted_plate(manager):
    assert manager.try_open_gate(1, "KRA12345") is True


def test_try_open_gate_not_whitelisted_plate(manager):
    assert manager.try_open_gate(1, "QWE12345") is False


def test_try_open_gate_none_plate(manager):
    assert manager.try_open_gate(1, None) is False


def test_is_pending_ids_working(manager):
    assert manager.try_open_gate(1, "KRA12345") is True
    assert manager.try_open_gate(1, "KRA12345") is False


def test_gate_failed_retry_cooldown(manager, clock):
    clock.now = 100.00

    assert manager.try_open_gate(1, "KRA12345") is True
    manager.report_attempt(1, False)

    clock.now = 104.00

    assert manager.try_open_gate(1, "KRA12345") is False

    clock.now = 106.00

    assert manager.try_open_gate(1, "KRA12345") is True


def test_success_open_cooldown(manager_two_plates, clock):
    clock.now = 100.00

    assert manager_two_plates.try_open_gate(1, "KRA12345") is True
    manager_two_plates.report_attempt(1, True)

    clock.now = 107.00

    assert manager_two_plates.try_open_gate(2, "KMY12345") is False

    clock.now = 110.00

    assert manager_two_plates.try_open_gate(2, "KMY12345") is True


def test_open_plate_after_success(manager, clock):
    clock.now = 100.00

    assert manager.try_open_gate(1, "KRA12345") is True
    manager.report_attempt(1, True)

    clock.now = 111.00

    assert manager.try_open_gate(1, "KRA12345") is False


def test_forget_track_opened_id(manager, clock):
    clock.now = 100.00

    assert manager.try_open_gate(1, "KRA12345") is True
    manager.report_attempt(1, True)

    manager.forget_track(1)

    clock.now = 111.00

    assert manager.try_open_gate(1, "KRA12345") is True


def test_forget_track_pending_id(manager):
    assert manager.try_open_gate(1, "KRA12345") is True

    manager.forget_track(1)

    assert manager.try_open_gate(1, "KRA12345") is True


def test_report_attempt_unknown_track(manager):
    with pytest.raises(ValueError):
        manager.report_attempt(1, True)
