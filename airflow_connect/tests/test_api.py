import json
import os
import tempfile
import shutil
import pytest

from importlib_resources import files
from airflow_connect.api import hack_manifest, trigger_deploy_or_rerun
from contextlib import contextmanager
from pathlib import Path


def test_hack_manifest(tmp_dir):
    p_manifest = files("airflow_connect") / "tests" / "rmd_report/manifest.json"
    p_notebook = files("airflow_connect") / "tests" / "rmd_report/report_rmd.Rmd"

    shutil.copy(p_manifest, tmp_dir)
    shutil.copy(p_notebook, tmp_dir)

    data = json.load(open(p_manifest))
    res = hack_manifest(data, p_notebook)
    assert "report_rmd.Rmd" in res["files"]


@pytest.mark.parametrize("notebook,req", [
    ("ipynb_report/test_report3.ipynb", "ipynb_report/requirements.txt"),
    ("rmd_report/report_rmd.Rmd", "rmd_report/manifest.json"),
])
def test_deploy_or_rerun(fs, notebook, req):
    p_notebook = files("airflow_connect") / "tests" / notebook
    p_reqs = files("airflow_connect") / "tests" / req
    res = trigger_deploy_or_rerun(fs, p_notebook, requirements_path = p_reqs)

    assert res["action"] == "new-deploy"

    res = trigger_deploy_or_rerun(fs, p_notebook, requirements_path = p_reqs)

    assert res["action"] == "re-render"

    with tempfile.TemporaryDirectory() as tmp_dir:
        p_tmp_nb = Path(tmp_dir) / p_notebook.name
        new_nb = p_notebook.read_text().replace("print(1 + 1)", "print(1 + 2)")
        p_tmp_nb.write_text(new_nb)

        res = trigger_deploy_or_rerun(fs, p_tmp_nb, requirements_path = p_reqs)

        assert res["action"] == "re-deploy"
