from airflow_connect import api
from pins.rsconnect.fs import RsConnectFs
from dotenv import load_dotenv

import logging
import sys

root = logging.getLogger("airflow_connect.api")
root.setLevel(logging.DEBUG)

if not len(root.handlers):
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

load_dotenv()

fs = RsConnectFs(server_url="http://localhost:3939")

api.trigger_deploy_or_rerun(fs, "test_report/test_report3.ipynb")
