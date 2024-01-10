import json
import os
import pathlib

import pytest
import yaml


@pytest.fixture
def datadir(request):
    return (
        pathlib.Path(os.path.realpath(__file__)).parent
        / os.path.splitext(request.module.__file__)[0]
    )


class Datadir:
    def __init__(self, datadir: pathlib.Path):
        self.datadir = datadir

    def load(self, filename: str):
        with open(self.datadir / filename) as f:
            match os.path.splitext(filename)[-1]:
                case ".json":
                    return json.load(f)
                case ".yaml":
                    return yaml.safe_load(f)


@pytest.fixture
def datadir_obj(datadir: pathlib.Path):
    return Datadir(datadir)


@pytest.fixture
def test_root():
    return pathlib.Path(os.path.realpath(__file__)).parent
