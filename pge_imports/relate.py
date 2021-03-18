from relate import *

import arcpy
import pandas as pd

# get parameters from ArcMap geoprocessing window
report_id = arcpy.GetParameter(0)
query_path = arcpy.GetParameterAsText(1)
batch_bool = arcpy.GetParameter(2)
batch_name = arcpy.GetParameterAsText(3)

# append resource relations to the batch tables
prim_df = pd.read_excel(query_path, 0)
tri_df = pd.read_excel(query_path, 1)
fs_df = pd.read_excel(query_path, 2)
other_df = pd.read_excel(query_path, 3)

prim_lst = [primary(row.county, row.id) for index, row in prim_df.iterrows()]
tri_lst = [trinomial(row.county, row.id) for index, row in tri_df.iterrows()]
fs_lst = [forest(row.f1, row.f2, row.f3, row.f4) for index, row in fs_df.iterrows()]
other_lst = [other(row.other_name) for index, row in other_df.iterrows()]

prim_bool = (len(prim_lst) > 0)
tri_bool = (len(tri_lst) > 0)
fs_bool = (len(fs_lst) > 0)
other_bool = (len(other_lst) > 0)

if report_id != 0:
    if prim_bool:
        for prim in prim_lst:
            append_relation(report_id, 'primary',
                            'primco', prim.county,
                            'primno', prim.id)

    if tri_bool:
        for tri in tri_lst:
            append_relation(report_id, 'trinomial',
                            'primco', tri.county,
                            'trinno', tri.id,
                            name = tri.name)

    if fs_bool:
        for fs in fs_lst:
            append_relation(report_id, 'forest',
                            'fsregion', fs.f1,
                            'fsforest', fs.f2,
                            'fsnump1', fs.f3,
                            'fsnump2', fs.f4)

    if other_bool:
        for oth in other_lst:
            append_relation(report_id, 'other',
                            'othername', oth.name)

if batch_bool:
    if prim_bool:
        for prim in prim_lst:
            append_to_batch(batch_name, 'primary',
                            'primco', prim.county,
                            'primno', prim.id)

    if tri_bool:
        for tri in tri_lst:
            append_to_batch(batch_name, 'trinomial',
                            'primco', tri.county,
                            'trinno', tri.id)

    if fs_bool:
        for fs in fs_lst:
            append_to_batch(batch_name, 'forest',
                            'fsregion', fs.f1,
                            'fsforest', fs.f2,
                            'fsnump1', fs.f3,
                            'fsnump2', fs.f4)
    
    if other_bool:
        for oth in other_lst:
            append_to_batch(batch_name, 'other',
                            'othername', oth.name)
