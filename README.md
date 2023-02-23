# airflow-posit-connect

An experimental airflow operator for executing content on Post Connect

## Install

```bash
pip install git+https://github.com/machow/airflow-posit-connect.git#egg=airflow_connect
```

## Usage

Currently,

```python
from airflow_connect.api import trigger_deploy_or_rerun
from pins.rsconnect.fs import RsConnectFs

# Note that you need to fill in the ... with credentials
fs = RsConnectFs(server_url=..., api_key=...)


trigger_deploy_or_rerun(
    fs,
    "airflow_connect/tests/ipynb_report/test_report3.ipynb",
    requirements_path="airflow_connect/tests/ipynb_report/requirements.txt"
)
```

## Develop

```bash
make airflow_connect/tests/rsconnect_keys.json
```

```python
from airflow_connect.api import trigger_deploy_or_rerun
from airflow_connect.tests.conftest import rsc_fs_from_key

# Note that you need to fill in the ... with credentials
fs = rsc_fs_from_key("admin")


trigger_deploy_or_rerun(
    fs,
    "airflow_connect/tests/ipynb_report/test_report3.ipynb",
    requirements_path="airflow_connect/tests/ipynb_report/requirements.txt"
)
```
