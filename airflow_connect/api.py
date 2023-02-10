import hashlib
import pendulum
import pins
import time
import tempfile
import tarfile
import subprocess

from pins.rsconnect.api import RsConnectApiMissingContentError


from datetime import datetime
from pathlib import Path

from requests.models import StreamConsumedError

import logging

_log = logging.getLogger(__name__)


def stream(r, api):
    # TODO: should log most of this as info
    print(r.status_code)
    if r.status_code == 204:
        print("\n\n=====\nreturning log instead======\n\n\n")
        r.request.url.replace("/tail", "/log")
        r_log = api._raw_query(r.request.url.replace("/tail", "/log"))
        print(r_log)

    try:
        for line in r.iter_lines():
            if line:
                print(line.decode())
    except StreamConsumedError:
        print("Stream consumed")


def fetch_pending_job(api, content, since):
    if isinstance(since, str):
        since = pendulum.parse(since)

    ii = 0
    start_time = since - pendulum.duration(days = 1)
    while start_time < since:
        print("Polling for job")
        time.sleep(1)
        ii += 1

        if ii > 30:
            raise NotImplementedError("Polling failed")

        jobs = api.get_content_item_jobs(content["guid"])
        last_job = jobs[0]
        
        start_time = pendulum.parse(last_job["start_time"])
        print("START TIME:", start_time)
        
    return last_job


def maybe_get_content(fs, content_name):
    # TODO: assumes we've already checked for existance
    try:
        content = fs.info(content_name)
        return content
    except RsConnectApiMissingContentError:
        return

        
def is_rerenderable(fs, notebook_path, content, debug=True):
    if content["bundle_id"] is None:
        _log.info("Cannot render: content does not have a bundle")
        return False

    notebook_path = Path(notebook_path)

    src_content = open(notebook_path, "rb").read()
    src_hash = hashlib.md5(src_content)

    with tempfile.TemporaryDirectory() as tmp_dir:
        p_archive = Path(tmp_dir) / "bundle.tar.gz"
        with open(p_archive, "wb") as f:
            fs.api.get_content_bundle_archive(
                content["guid"],
                content["bundle_id"],
                f
            )

        tar = tarfile.open(p_archive, "r:gz")
        tar.extractall(path=tmp_dir)
        tar.close()

        dst_content = open(f"{tmp_dir}/{notebook_path.name}", "rb").read()

    if src_content != dst_content:
        _log.info("Cannot render: source content contains changes")
        if debug:
            _log.debug("Logging diff")
            for li in difflib.ndiff(src_content, dst_content):
                _log.debug(li)

        return False

    return True



def trigger_rerun(fs, content):
    # TODO: clean up variable
    info = content

    variants = fs.api.get_applications_item_variants(info["id"])

    variant_id = variants[0]["id"]
    now = pendulum.now("UTC").at(hour=None, minute=None, second=None)
    print("NOW:", now)
    task = fs.api.post_variant_render(variant_id)

    job = fetch_pending_job(fs.api, info, since=now)

    log = fs.api.get_content_item_jobs_item_tail(info["guid"], job["key"])
    stream(log, fs.api)

    # TODO: also need to check job exit status
    #task_result = fs.api.wait_for_task(task["id"])

    return task, job


def trigger_deploy(notebook_path, new=False, use_tempdir=False):
    from rsconnect.main import cli

    # Case 1: deploying from a temporary directory ============================
    # in this case, we copy to tempdir, and then recurse.
    if use_tempdir:
        with tempfile.TemporaryDirectory() as tmp_dir:
            dst_fname = shutil.copy(self.file_path, tmp_dir)

            return trigger_deploy(dst_fname, new=new, use_tempdir=False)


    # Case 2: deploying from non-temp dir =====================================

    notebook_path = Path(notebook_path)

    new_arg = ["--new"] if new else []

    if notebook_path.name.endswith(".Rmd") or notebook_path.name.endswith(".Rmarkdown"):
        _log.info("Running the R rsconnect package to create Rmarkdown manifest.")
        # TODO: note that dir_path is injected into an R script, which could
        # technically be exploited to execute arbitrary R code.
        subprocess.run([
            "Rscript",
            "-e",
            f'''rsconnect::writeManifest("{notebook_path.parent}", "{notebook_path.name}")'''
        ])

        p_manifest = notebook_path.parent / "manifest.json"
        cli_args = ["deploy", "manifest", *new_arg, str(p_manifest)]
    else:
        cli_args = ["deploy", "notebook", *new_arg, str(notebook_path)]

    try:
        cli(cli_args)
    except SystemExit as e:
        if e.args[0] != 0:
            raise Exception(f"System exited with code: {e}")


def trigger_deploy_or_rerun(fs, notebook_path, user_name = "admin"):
    notebook_path = Path(notebook_path).absolute()
    notebook_name = notebook_path.name.rsplit(".")[0]
    content_name = f"{user_name}/{notebook_name}"

    content = maybe_get_content(fs, content_name)

    if content is None:
        print("Deploying new ----")
        trigger_deploy(notebook_path, new = True)

    elif is_rerenderable(fs, notebook_path, content):
        print("Rerunning ----")
        trigger_rerun(fs, content)

    else:
        print("Re-deploying ----")
        trigger_deploy(notebook_path, new = False)
