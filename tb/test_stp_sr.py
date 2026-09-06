import pytest

from _harness import RTL, run


@pytest.mark.parametrize("width", [8, 12])
def test_stp_sr(width, waves):
    run("stp_sr", [RTL / "sensor" / "stp_sr.sv"], {"WIDTH": width}, waves)
