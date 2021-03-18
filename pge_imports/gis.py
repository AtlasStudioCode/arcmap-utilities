import arcpy, os
import pandas as pd

# import all classes
import sys
sys.path.append("U:/scripts/")
from classes import *

# create an edit object
edit = Edit()

# read cultural resource constraints report excel worksheet as a pandas dataframe
df = pd.read_excel("crcr.xlsx", 0)

# delete old rows of temp edit gdb
arcpy.DeleteRows_management(edit.report_point)
arcpy.DeleteRows_management(edit.report_line)
arcpy.DeleteRows_management(edit.report_area)

# add gis to temp edit gdb
for index, row in df.iterrows():
    edit.append(row["gispath"], row["uid"])
