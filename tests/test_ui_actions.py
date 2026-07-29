from xadrez_das_lendas.ui_actions import UIAction
from xadrez_das_lendas.ui_screens import ScreenPainter


class FakeRect:
    def __init__(self, hit: bool) -> None:
        self.hit = hit

    def collidepoint(self, _position):
        return self.hit


def test_screen_actions_are_exposed_without_button_names():
    painter = ScreenPainter.__new__(ScreenPainter)
    painter._actions = {
        UIAction.START_CAMPAIGN: FakeRect(False),
        UIAction.QUIT: FakeRect(True),
    }

    assert painter.action_at((10, 20)) == UIAction.QUIT

    painter.begin_frame()
    assert painter.action_at((10, 20)) is None
