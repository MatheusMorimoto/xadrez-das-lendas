from xadrez_das_lendas.state import (
    WIN_TRANSITION_MS,
    WRONG_MOVE_RESET_MS,
    GameState,
    ScreenState,
)


def test_winning_move_schedules_transition():
    state = GameState()
    state.start_phase(1)

    assert state.move((3, 7), (6, 7), now_ms=100)
    assert state.transition_at == 100 + WIN_TRANSITION_MS
    assert not state.transition_ready(state.transition_at - 1)
    assert state.transition_ready(state.transition_at)

    state.consume_transition()
    assert state.transition_at is None


def test_wrong_move_uses_named_reset_duration():
    state = GameState()
    state.start_phase(1)

    assert not state.move((3, 7), (4, 7), now_ms=100)
    assert state.reset_at == 100 + WRONG_MOVE_RESET_MS


def test_campaign_progresses_and_finishes_after_video_sequences():
    state = GameState()
    state.start_phase(1)

    state.finish_video_sequence()
    assert state.phase_number == 2
    assert state.screen == ScreenState.PLAYING

    state.finish_video_sequence()
    assert state.phase_number == 3
    assert state.screen == ScreenState.PLAYING

    state.finish_video_sequence()
    assert state.phase_number == 4
    assert state.screen == ScreenState.PLAYING

    state.finish_video_sequence()
    assert state.phase_number == 4
    assert state.screen == ScreenState.FINISHED


def test_first_phase_victory_image_lasts_ten_seconds():
    state = GameState()
    state.start_phase(1)
    state.show_victory_image(500)

    assert state.screen == ScreenState.VICTORY_IMAGE
    assert state.victory_image_until == 10_500
    assert not state.victory_image_ready(10_499)
    assert state.victory_image_ready(10_500)


def test_phase_intro_clears_pending_timers_and_starts_selected_phase():
    state = GameState(reset_at=100, transition_at=200)

    state.show_phase_intro(2)
    assert state.screen == ScreenState.PHASE_INTRO
    assert state.phase_number == 2
    assert state.reset_at is None
    assert state.transition_at is None

    state.start_phase(state.phase_number)
    assert state.screen == ScreenState.PLAYING
    assert state.phase_number == 2
