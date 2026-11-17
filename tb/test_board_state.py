from _harness import RTL, run


def test_board_state(waves):
    run("board_state", [RTL / "caissa_pkg.sv", RTL / "game_state" / "board_state.sv"], waves=waves)
