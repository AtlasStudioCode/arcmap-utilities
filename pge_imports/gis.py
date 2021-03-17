import arcpy, os
import pandas as pd

import sys
sys.path.append("U:/scripts/")
from classes import *
                
edit = Edit()

crcr_xlsx = "crcr.xlsx"

df = pd.read_excel(crcr_xlsx, 0)

# delete old rows of temp edit gdb

arcpy.DeleteRows_management(edit.report_point)
arcpy.DeleteRows_management(edit.report_line)
arcpy.DeleteRows_management(edit.report_area)

# add gis to temp edit gdb

for index, row in df.iterrows():
    edit.append(row["gispath"], row["uid"])
