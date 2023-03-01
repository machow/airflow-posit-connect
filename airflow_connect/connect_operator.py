import os
import contextlib

from airflow.models import BaseOperator
from airflow_connect import api
from airflow.models import Variable

from pins.rsconnect.fs import RsConnectFs


# TODO: this allows us to temporarily set environment variables that will be
# used when calling the R rsconnect package (e.g. CONNECT_SERVER), but it is
# also very hacky.

@contextlib.contextmanager
def set_env(**kwargs):
    """
    Temporarily set the process environment variables.
    """
    old_environ = dict(os.environ)
    for k, v in kwargs.items():
        os.environ[k] = v

    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


class ConnectOperator(BaseOperator):

    def __init__(
        self,
        file_path,
        requirements_path = None,
        environment = None,
        **kwargs
    ):
        self.file_path = file_path
        self.requirements_path = requirements_path
        self.environment = environment or {}
        super().__init__(**kwargs)

    def execute(self, context):
        # TODO: pins should automatically look for this variable
        connect_server = Variable.get("connect_server")
        connect_api_key = Variable.get("connect_api_key")

        with set_env(CONNECT_SERVER=connect_server, CONNECT_API_KEY=connect_api_key):

            fs = RsConnectFs(
                server_url=connect_server,
                api_key=connect_api_key,
            )

            api.trigger_deploy_or_rerun(
                fs,
                self.file_path,
                requirements_path = self.requirements_path,
                environment = self.environment
            )
