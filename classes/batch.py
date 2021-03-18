import arcpy, os
import pandas as pd

from arcpy import AddMessage as msg
from arcpy import AddFieldDelimiters as afd

from mxd import Mxd

class Batch(Mxd):
    # class to represent a batch session of an enterprise geodatabase
    def __init__(self, name):
        # initalize the batch class properties
        Mxd.__init__(self)

        self.batch = self.set_table("batch")
        self.batch_resource = self.set_table("batchresource")
        self.batch_report = self.set_table("batchreport")
        self.resource_report_events = self.set_table("resourcereportevents")
        
        self.name = name
        self.gid = self.set_gid()

    def set_gid(self):
        # set the global id for the batch object by querying the batch table
        query = """{0} = '{1}'""".format(afd(self.batch.dataSource, "batchname"), self.name)
        with arcpy.da.SearchCursor(self.batch.dataSource, "globalid", query) as cursor:
            return [row[0] for row in cursor][0]

    def add_record(self, record_type, ids):
        # add a resource or report to the batch
        table = {"resource": self.batch_resource,
                 "report": self.batch_report}[record_type]
        uid = {"resource": "resourceid",
               "report": "reportid"}[record_type]

        edit = arcpy.da.Editor(table.workspacePath)
        edit.startEditing(False, True)
        edit.startOperation()

        with arcpy.da.InsertCursor(table.dataSource, ["batchid", uid]) as cursor:
                for i in ids:
                    cursor.insertRow((self.gid, i))

        edit.stopOperation()
        edit.stopEditing(True)

    def add_relate(self, row):
        # add a resource relationship to the relationship table
        report_id = row["reportid"]
        dup_bool = False

        if not pd.isnull(row["primco"]):
            f1 = afd(self.resources.dataSource, "primco")
            f2 = afd(self.resources.dataSource, "primno")
            v1 = row["primco"]
            v2 = row["primno"]
            expr = """{} = {} AND {} = {}""".format(f1, v1, f2, v2)
        elif not pd.isnull(row["trinco"]):
            f1 = afd(self.resources.dataSource, "trinco")
            f2 = afd(self.resources.dataSource, "trinno")
            v1 = row["trinco"]
            v2 = row["trinno"]
            expr = """{} = {} AND {} = {}""".format(f1, v1, f2, v2)
        elif not pd.isnull(row["fs1"]):
            f1 = afd(self.resources.dataSource, "fsregion")
            f2 = afd(self.resources.dataSource, "fsforest")
            f3 = afd(self.resources.dataSource, "fsnump1")
            f4 = afd(self.resources.dataSource, "fsnump2")
            v1 = row["fs1"]
            v2 = row["fs2"]
            v3 = row["fs3"]
            v4 = row["fs4"]
            expr = """{} = {} AND {} = {} AND {} = {} AND {} = {}""".format(f1, v1, f2, v2,
                                                                            f3, v3, f4, v4)
        elif not pd.isnull(row["othername"]):
            f1 = afd(self.resources.dataSource, "othername")
            v1 = row["othername"]
            expr = """{} = {}""".format(f1, v1)
        
        with arcpy.da.SearchCursor(self.resources.dataSource, 'resourceid', expr) as cursor:
            try:
                resource_ids = [row[0] for row in cursor]
            except Exception:
                resource_ids = None

        if resource_ids:
            edit = arcpy.da.Editor(self.resource_report_events.workspacePath)
            edit.startEditing(False, True)
            edit.startOperation()

            with arcpy.da.InsertCursor(self.resource_report_events.dataSource, ['reportid', 'resourceid']) as cursor:
                for resource_id in resource_ids:
                    cursor.insertRow((report_id, resource_id))

            edit.stopOperation()
            edit.stopEditing(True)
            
            if len(resource_ids) > 1:
                dup_bool = True
            
        return dup_bool, resource_ids

    
    def delete_gis(self, gids, feat_name):
        # delete all features associated with the global id
        lyr = {"ResourcePoint": self.resource_point,
               "ResourceLine": self.resource_line,
               "ResourceArea": self.resource_area,
               "ReportPoint": self.report_point,
               "ReportLine": self.report_line,
               "ReportArea": self.report_area}[feat_name]
        
        expression = """{0} IN ({1})""".format(afd(lyr), "globalid",
                                               ",".join([str(i) for i in gids]))

        lyr.defintionQuery = None

        arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", expression)
        if int(arcpy.GetCount_management(lyr)[0]) > 0:
            arcpy.DeleteRows_management(lyr)
