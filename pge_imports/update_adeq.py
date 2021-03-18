import arcpy, os, time
import pandas as pd

from arcpy import AddFieldDelimiters as afd
from arcpy import AddMessage as msg

# import all classes
import sys
sys.path.append("U:/scripts/")
from classes import *

# get list of files in input folder
folder = arcpy.GetParameterAsText(0)
files = [os.path.join(folder, f) for f in os.listdir(folder)]

# create dataframe for unique report id and adequacy
df = pd.DataFrame({"ureportid": [],
                   "adeq": []})

# get the current adequacy from the input excel files
for f in files:
    try:
        idf = pd.read_excel(f, 1)
    except Exception:
        idf = pd.read_excel(f, 0)

    if idf["Contractor Adequacy"].isnull().all():
        idf["adeq"] = idf["surveyadeq"]
    else:
        idf["adeq"] = idf["Contractor Adequacy"]
        
    idf["adeq"] = idf.apply(lambda row: row["adeq"].title(), axis = 1)

    df = df.append(pd.DataFrame({"ureportid": idf["ureportid"],
                                 "adeq": idf["adeq"]}), ignore_index = True)
id_dict = dict(zip(df["ureportid"], df["adeq"]))

# create a map document object and query the reports for only those with report ids in the above dictionary
mxd = Mxd()
def_query = """{0} IN ({1})""".format(afd(mxd.reports.dataSource, "reportid"),
                                      ",".join([str(i) for i in df["ureportid"]]))
mxd.reports.definitionQuery = def_query
arcpy.RefreshActiveView()
time.sleep(5)

# update the adequacy field of the reports by their report id
try:
    edit = arcpy.da.Editor(mxd.reports.workspacePath)

    edit.startEditing(False, True)
    edit.startOperation()

    with arcpy.da.UpdateCursor(mxd.reports, ["reportid", "surveyadeq"]) as cursor:
        for row in cursor:
            adeq = id_dict[row[0]]
            if not pd.isnull(adeq):
                row[1] = adeq
                cursor.updateRow(row)

    edit.stopOperation()
    edit.stopEditing(True)
                
except arcpy.ExecuteError:
    msg("Editing error.")
