import arcpy, os
import pandas as pd

import sys
sys.path.append("../")
from classes import *

del_csv = "del.csv"
del_df = pd.read_csv(del_csv)

dup_csv = "dup.csv"
dup_df = pd.read_csv(dup_csv)

name = arcpy.GetParameterAsText(0)

batch = Batch(name)

batch.add(dup_df["recordid"]["Resource" in dup_df["feat_name"]].tolist(), "resource")
batch.add(dup_df["otherid"]["Resource" in dup_df["feat_name"]].tolist(), "resource")

batch.add(dup_df["recordid"]["Report" in dup_df["feat_name"]].tolist(), "report")
batch.add(dup_df["otherid"]["Report" in dup_df["feat_name"]].tolist(), "report")

feat_names = del_df["feat_name"].unique().tolist()
for feat_name in feat_names:
    batch.delete(del_df["globalid"][del_df["feat_name"] == feat_name].tolist(), feat_name)

del_df = pd.DataFrame({"globalid": [],
                       "feat_name": []})

dup_df = pd.DataFrame({"recordid": [],
                       "feat_name": [],
                       "otherid": []})

del_df.to_csv(del_csv, index = False)
dup_df.to_csv(dup_csv, index = False)
