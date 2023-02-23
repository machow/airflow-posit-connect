from api import trigger_deploy_or_rerun

def _attach_logger():
    import logging
    import sys

    root = logging.getLogger("airflow_connect")
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)


def main():
    import sys

    url, api_key, notebook_path, user_name = sys.argv[1:5]

    _attach_logger()

    #fs = RsConnectFs(server_url=url, api_key=api_key)

    #trigger_deploy_or_rerun(fs, notebook_path, user_name)
    raise NotImplementedError()

