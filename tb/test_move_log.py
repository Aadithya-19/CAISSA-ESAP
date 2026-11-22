from _harness import RTL, run


def test_move_log(waves):
    run("move_log", [RTL / "caissa_pkg.sv", RTL / "game_state" / "move_log.sv"], waves=waves)
