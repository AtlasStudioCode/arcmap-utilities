import arcpy, os, shutil
import pandas as pd

from arcpy import AddMessage as msg

import sys
sys.path.append("U:/scripts/")
from classes import *

arcpy.env.overwriteOutput = True

work_loc = arcpy.GetParameterAsText(0)
linear_unit = arcpy.GetParameterAsText(1)
search_area = arcpy.GetParameterAsText(2)

project = Project(work_loc, linear_unit, search_area)

extract = Extract(project, Default())

request = Request(project, extract)

