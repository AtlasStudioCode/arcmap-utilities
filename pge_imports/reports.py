import arcpy, os
import pandas as pd
from datetime import datetime, timedelta

from arcpy import AddFieldDelimiters as afd
from arcpy import AddMessage as msg

import sys
sys.path.append("U:/scripts/")
from classes import *

crcr_xlsx = "crcr.xlsx"

edit_gdb = "gis_temp.gdb"
edit_point = os.path.join("Report", "ReportPoint")
edit_line = os.path.join("Report", "ReportLine")
edit_area = os.path.join("Report", "ReportArea")

batch_name = arcpy.GetParameterAsText(0)
batch = Batch(batch_name)

# create dataframe

df = pd.read_excel(crcr_xlsx, 0)

df["label"] = df.apply(lambda row: row["last_name"] + " " + str(row["year"]), axis = 1)
df["reporttitle"] = df.apply(lambda row: row["report_name"] + " " + str(row["report_num"]), axis = 1)
df["prepared_for"] = "PG&E"
df["temptitle"] = df.apply(lambda row: os.path.basename(os.path.dirname(row["origpath"])), axis = 1)

# add reports

msg("Adding reports to table...")

fields = ["label", "reporttitle", "temptitle",
          "year", "author", "agencycompany",
          "origpath", "reporttype", "prepared_for"]

edit = arcpy.da.Editor(batch.reports.workspacePath)
edit.startEditing(False, True)
edit.startOperation()

with arcpy.da.InsertCursor(batch.reports.dataSource, fields) as cursor:
    for index, row in df.iterrows():
        values = (row["label"], row["reporttitle"], row["temptitle"],
                  row["year"], row["author"], row["agencycompany"],
                  row["origpath"], row["reporttype"], row["prepared_for"])
        cursor.insertRow(values)

edit.stopOperation()
edit.stopEditing(True)

# get report_ids for new report rows

msg("Adding reports to batch...")

now = datetime.now()
now = now + timedelta(hours = 7) - timedelta(minutes = 1)
dt_exp = now.strftime("%Y-%m-%d %H:%M:%S")

query = """{} = '{}' AND {} > '{}'""".format(afd(batch.reports.dataSource, "created_user"), "DANIEL",
                                         afd(batch.reports.dataSource, "created_date"), dt_exp)

with arcpy.da.SearchCursor(batch.reports.dataSource, ["reportid"], query) as cursor:
    rep_ids = [int(row[0]) for row in cursor]

df["reportid"] = rep_ids

# add reports to batch

batch.add_record("report", df["reportid"].tolist())

# apply attributes and add gis

msg("Adding GIS to layers...")

def set_feattype(comment, fc):
    if fc == edit_point:
        return "ProjectPt"
    elif fc == edit_line:
        return "ProjectCL"
    elif fc == edit_area:
        if comment in ("Intensive", "intensive",
                       "Recon", "recon",
                       "Nonintensive", "nonintensive",
                       "Survey", "survey",
                       "Unsurveyed", "unsurveyed"):
            return "SurvBnd"
        else:
            return "ProjectArea"

def apply_attr(fc):
    fields = ["uid", "reportid", "reportlabel",
              "source", "confidence", "contractor",
              "feattype", "comment"]
    with arcpy.da.UpdateCursor(fc, fields) as cursor:
        for feat in cursor:
            for index, row in df.iterrows():
                if int(feat[0]) == row["uid"]:
                    feat[1] = row["reportid"]
                    feat[2] = row["label"]
                    if pd.isnull(row["gispath"]):
                        dir_bool = False
                    else:
                        dir_bool = os.path.isdir(row["gispath"])
                    feat[3] = "ImportedClientData" if dir_bool else "DigUSGS24k"
                    feat[4] = "Good" if dir_bool else "Approximate"
                    feat[5] = row["agencycompany"]
                    feat[6] = set_feattype(feat[7], fc)
                    cursor.updateRow(feat)

arcpy.env.workspace = edit_gdb

edit = arcpy.da.Editor(edit_gdb)
edit.startEditing(False, True)
edit.startOperation()

apply_attr(edit_point)
apply_attr(edit_line)
apply_attr(edit_area)

edit.stopOperation()
edit.stopEditing(True)

arcpy.Append_management(edit_point, batch.report_point, "NO_TEST")
arcpy.Append_management(edit_line, batch.report_line, "NO_TEST")
arcpy.Append_management(edit_area, batch.report_area, "NO_TEST")

# add relates

msg("Adding relates to reports...")

rel_dict = dict(zip(df["uid"], df["reportid"]))

rel = pd.read_excel(crcr_xlsx, 1)
rel["reportid"] = rel.apply(lambda row: rel_dict[row["uid"]], axis = 1)

for index, row in rel.iterrows():
    dup_bool, resource_ids = batch.add_relate(row)
    if dup_bool:
        batch.add_record("resource", resource_ids)
