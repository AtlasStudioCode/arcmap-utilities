import arcpy, os
import pandas as pd

# import all classes
import sys
sys.path.append("U:/scripts/")
from classes import *

def SendEdits(gdb):
    # output two csv files to track duplicate records and deleted records
    mxd = Mxd()
    
    del_csv = "del.csv"
    del_df = pd.read_csv(del_csv)

    dup_csv = "dup.csv"
    dup_df = pd.read_csv(dup_csv)

    product_fld = os.path.dirname(gdb)
    
    base_csv = os.path.join(product_fld, "base.csv")
    base_df = pd.read_csv(base_csv)

    def append_edits(record_lyrs, uid):
        # utility function to compare lists of ids for duplicates and deleted values
        for lyr in record_lyrs:
            with arcpy.da.SearchCursor(fc, [uid, "globalid"]) as cursor:
                edit_ids = [row[0] for row in cursor]
                edit_gids = [row[1] for row in cursor]
                
            base_gids = base_df["globalid"][base_df["feat_name"] == fc.name]
            base_ids = base_df["recordid"][base_df["feat_name"] == fc.name]
            
            del_gids = [i for i in base_gids if i not in edit_gids]
            dup_ids = [i for i in base_ids if i not in edit_ids]
            
            append_del_df = pd.DataFrame({"globalid": del_ids})
            append_del_df["feat_name"] = lyr.name
            
            append_dup_df = pd.DataFrame({"recordid": dup_ids})
            append_dup_df["feat_name"] = lyr.name
            append_dup_df["otherid"] = 0
            
            del_df = del_df.append(append_del_df, ignore_index = True)
            dup_df = dup_df.append(append_dup_df, ignore_index = True)

    append_edits(mxd.resource_lyrs, "resourceid")
    append_edits(mxd.report_lyrs, "reportid")

    del_df.to_csv(del_csv, index = False)
    dup_df.to_csv(dup_csv, index = False)
    os.remove(base_csv)
