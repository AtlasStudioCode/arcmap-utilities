# import modules
import arcpy, os, shutil
import pandas as pd

# import functions
from products import *

# get parameters
gdb = arcpy.GetParameterAsText(0)

kmz_bool = arcpy.GetParameter(1)
pdf_bool = arcpy.GetParameter(2)
shp_bool = arcpy.GetParameter(3)

create_products(gdb, kmz_bool, pdf_bool, shp_bool)
