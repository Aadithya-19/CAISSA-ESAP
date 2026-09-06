import pytest


def pytest_addoption(parser):
    parser.addoption("--waves", action="store_true", help="dump an FST per test")


@pytest.fixture
def waves(request):
    return request.config.getoption("--waves")
