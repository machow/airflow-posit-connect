import os
import shutil
import tempfile

from airflow.operators.bash_operator import BashOperator
from contextlib import contextmanager
from pathlib import Path

rmd_command_template = """
Rscript -e 'rmarkdown::render("{file_path}", run_pandoc=FALSE)' || exit 1; rm -f {rendered_output}
"""

rsc_command_template = """
cd 
ls
Rscript -e 'print(list.files()); rsconnect::writeManifest("{dir_path}", "{file_path}")'
rsconnect deploy manifest {manifest_path}
"""

@contextmanager
def chdir(new_dir):
    prev = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(prev)


class ConnectOperator(BashOperator):
    """
    """
    ui_color = "#75AADB"

    # gusty gives us a file_path for free
    def __init__(self, file_path, tempdir=True, *args, **kwargs):
        self.file_path = file_path
        self.rendered_output = self.file_path.replace('.Rmd', '.knit.md')
        self.tempdir = tempdir


        #command = rsc_command_template.format(file_path = self.file_path,
        #                                  rendered_output = self.rendered_output)
        super().__init__(bash_command = "PLACEHOLDER", *args, **kwargs)

    def execute(self, context):
        with tempfile.TemporaryDirectory() as tmp_dir:
            dst_fname = shutil.copy(self.file_path, tmp_dir)

            # Hack to move everything into a temporary directory
            p_file = Path(dst_fname)
            p_manifest = p_file.parent / "manifest.json"

            self.bash_command = rsc_command_template.format(
                dir_path = str(p_file.parent),
                file_path = p_file.name,
                manifest_path = p_manifest,
                rendered_output = self.rendered_output
            )


            with chdir(tmp_dir):
                super().execute(context)
