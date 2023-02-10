# ---
# ---

from tidypal.utils import copy_to_warehouse

from siuba.data import mtcars
import os
print(os.environ["PIPELINE_WAREHOUSE_URI"])

copy_to_warehouse(mtcars, "mtcars")
