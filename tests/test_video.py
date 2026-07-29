from pathlib import Path

from xadrez_das_lendas import video
from xadrez_das_lendas.video import VideoPlayer


class FakeCapture:
    def __init__(self, opened: bool) -> None:
        self._opened = opened
        self.released = False

    def isOpened(self):
        return self._opened

    def read(self):
        return False, None

    def release(self):
        self.released = True


class FakeCV2:
    def __init__(self, invalid_names=()) -> None:
        self.invalid_names = set(invalid_names)
        self.opened: list[str] = []

    def VideoCapture(self, path):
        name = Path(path).name
        self.opened.append(name)
        return FakeCapture(name not in self.invalid_names)


class FakeMixer:
    @staticmethod
    def get_init():
        return False


class FakePygame:
    mixer = FakeMixer()


def test_video_player_skips_missing_and_invalid_files(monkeypatch, tmp_path):
    (tmp_path / "invalid.mp4").touch()
    (tmp_path / "valid.mp4").touch()
    monkeypatch.setattr(video, "asset_path", lambda name, required=False: tmp_path / name)
    cv2 = FakeCV2({"invalid.mp4"})
    player = VideoPlayer(cv2_module=cv2, pygame_module=FakePygame())

    assert player.start(("missing.mp4", "invalid.mp4", "valid.mp4"))
    assert cv2.opened == ["invalid.mp4", "valid.mp4"]
    assert player.active

    player.stop()
    assert not player.active


def test_video_player_advances_through_a_sequence(monkeypatch, tmp_path):
    for name in ("one.mp4", "two.mp4"):
        (tmp_path / name).touch()
    monkeypatch.setattr(video, "asset_path", lambda name, required=False: tmp_path / name)
    cv2 = FakeCV2()
    player = VideoPlayer(cv2_module=cv2, pygame_module=FakePygame())

    assert player.start(("one.mp4", "two.mp4"))
    assert player.next_surface((640, 640)) is None
    assert cv2.opened == ["one.mp4", "two.mp4"]
    assert not player.active
