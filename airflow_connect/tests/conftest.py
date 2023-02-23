import os
import pytest
import tempfile
import json

from contextlib import contextmanager
from pathlib import Path
from importlib_resources import files

from pins.rsconnect.fs import RsConnectFs
from pins.tests.helpers import rsc_delete_user_content


@contextmanager
def chdir(new_dir):
    prev = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(prev)


def rsc_fs_from_key(name):
    key_path = files("airflow_connect") / "tests" / "rsconnect_keys.json"
    api_key = json.load(open(key_path))[name]
    fs = RsConnectFs(
        server_url="http://localhost:9082",
        api_key=api_key
    )

    return fs



@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmp, chdir(tmp):
        yield Path(tmp)


@pytest.fixture(scope="session")
def fs():
    fs = rsc_fs_from_key("admin")
    yield fs

    rsc_delete_user_content(fs.api)
