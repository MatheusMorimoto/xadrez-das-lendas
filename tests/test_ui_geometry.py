from xadrez_das_lendas.ui_geometry import board_square


def test_board_square_normal_and_inverted():
    position = (40 + 3 * 80 + 10, 40 + 2 * 80 + 10)
    assert board_square(position, cell=80, margin=40, inverted=False) == (2, 3)
    assert board_square(position, cell=80, margin=40, inverted=True) == (5, 3)


def test_board_square_rejects_margins_and_outside_positions():
    assert board_square((39, 40), cell=80, margin=40, inverted=False) is None
    assert board_square((40, 39), cell=80, margin=40, inverted=False) is None
    assert board_square((680, 40), cell=80, margin=40, inverted=False) is None
    assert board_square((40, 680), cell=80, margin=40, inverted=False) is None
