from xadrez_das_lendas.paths import asset_path, validate_assets
from xadrez_das_lendas.phases import PHASES, get_phase
from xadrez_das_lendas.rules import legal_moves
from xadrez_das_lendas.state import GameState, ScreenState


def all_required_assets():
    names = {setup.asset for phase in PHASES.values() for setup in phase.pieces}
    names |= {video for phase in PHASES.values() for video in phase.videos}
    names |= {phase.victory_image for phase in PHASES.values() if phase.victory_image}
    names |= {f"{video.removesuffix('.mp4')}.ogg" for phase in PHASES.values() for video in phase.videos}
    names.add("tela_inicio.jpeg")
    return names


def test_all_phases_are_structurally_valid():
    for phase in PHASES.values():
        board = phase.create_board()
        assert board.validate() == []
        assert len({piece.square for piece in board.pieces}) == len(board.pieces)


def test_first_phase_uses_black_player_perspective():
    assert get_phase(1).turn == "preta"
    assert get_phase(1).inverted is True


def test_all_required_assets_exist_with_exact_case():
    assert validate_assets(all_required_assets()) == []
    for name in all_required_assets():
        assert asset_path(name).name == name


def test_each_phase_has_a_winning_move():
    expected = {
        1: ((3, 7), (6, 7)),
        2: ((1, 4), (1, 7)),
        3: ((5, 7), (6, 5)),
        4: ((4, 5), (3, 6)),
    }
    for number, (origin, target) in expected.items():
        state = GameState()
        state.start_phase(number)
        assert target in legal_moves(state.board.piece_at(origin), state.board)
        assert state.move(origin, target)
        assert state.screen == ScreenState.TRANSITION


def test_wrong_move_schedules_and_performs_reset():
    state = GameState()
    state.start_phase(1)
    assert not state.move((3, 7), (4, 7), now_ms=100)
    assert state.reset_at == 3100
    state.update(3099)
    assert state.board.piece_at((4, 7)) is not None
    state.update(3100)
    assert state.board.piece_at((3, 7)) is not None
    assert state.reset_at is None


def test_phase_intro_and_return_to_menu_are_real_states():
    state = GameState()
    state.show_phase_intro(2)
    assert state.screen == ScreenState.PHASE_INTRO
    state.start_phase(2)
    assert state.screen == ScreenState.PLAYING
    state.return_to_menu()
    assert state.screen == ScreenState.MENU
    assert state.phase_number == 1


def test_about_screen_and_return_to_menu():
    state = GameState()
    state.show_about()
    assert state.screen == ScreenState.ABOUT

    state.return_to_menu()
    assert state.screen == ScreenState.MENU


def test_phase_three_objective_is_configured_not_hardcoded_in_state():
    phase = get_phase(4)
    assert phase.objective == "target"
    assert phase.target_piece == "rainha"
    assert phase.target_square == (3, 6)
