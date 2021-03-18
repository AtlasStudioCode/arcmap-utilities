import arcpy, os
import pandas as pd

# import all classes
import sys
sys.path.append("../")
from classes import *

# read delete and duplicate csv files as pandas dataframes
del_df = pd.read_csv("del.csv")
dup_df = pd.read_csv("dup.csv")

# get the batch name parameter and create a batch object
name = arcpy.GetParameterAsText(0)
batch = Batch(name)

# add the duplicate resources and reports to the batch
batch.add(dup_df["recordid"]["Resource" in dup_df["feat_name"]].tolist(), "resource")
batch.add(dup_df["otherid"]["Resource" in dup_df["feat_name"]].tolist(), "resource")
batch.add(dup_df["recordid"]["Report" in dup_df["feat_name"]].tolist(), "report")
batch.add(dup_df["otherid"]["Report" in dup_df["feat_name"]].tolist(), "report")

# delete the provided features from the batch
feat_names = del_df["feat_name"].unique().tolist()
for feat_name in feat_names:
    batch.delete(del_df["globalid"][del_df["feat_name"] == feat_name].tolist(), feat_name)

# return empty delete and duplicate csv files
del_df = pd.DataFrame({"globalid": [],
                       "feat_name": []})
dup_df = pd.DataFrame({"recordid": [],
                       "feat_name": [],
                       "otherid": []})
del_df.to_csv(del_csv, index = False)
dup_df.to_csv(dup_csv, index = False)
