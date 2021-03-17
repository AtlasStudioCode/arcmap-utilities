import arcpy, os, shutil

from arcpy import AddMessage as msg
from arcpy import AddFieldDelimiters as afd

class Extract:
    def __init__(self, project, default):
        msg("Creating extract geodatabase...")
        
        self.gdb = self.set_gdb(project)

        self.resource_ds = os.path.join(self.gdb, "Resource")
        self.report_ds = os.path.join(self.gdb, "Report")
        
        self.resources = os.path.join(self.gdb, "resources")
        self.reports = os.path.join(self.gdb, "reports")

        self.resource_point = self.set_layer("ResourcePoint", "resource")
        self.resource_line = self.set_layer("ResourceLine", "resource")
        self.resource_area = self.set_layer("ResourceArea", "resource")
        self.resource_lyrs = [self.resource_point,
                              self.resource_line,
                              self.resource_area]

        self.report_point = self.set_layer("ReportPoint", "report")
        self.report_line = self.set_layer("ReportLine", "report")
        self.report_area = self.set_layer("ReportArea", "report")
        self.report_lyrs = [self.report_point,
                            self.report_line,
                            self.report_area]

        self.resource_point_relation = self.set_relation("Resource", "Point")
        self.resource_line_relation = self.set_relation("Resource", "Line")
        self.resource_area_relation = self.set_relation("Resource", "Area")

        self.report_point_relation = self.set_relation("Report", "Point")
        self.report_line_relation = self.set_relation("Report", "Line")
        self.report_area_relation = self.set_relation("Report", "Area")

        self.rec_lyr_dict = {default.resource_point: self.resource_point,
                             default.resource_line: self.resource_line,
                             default.resource_area: self.resource_area,
                             default.report_point: self.report_point,
                             default.report_line: self.report_line,
                             default.report_area: self.report_area}
        self.rec_relation_dict = {default.resource_point: self.resource_point_relation,
                                  default.resource_line: self.resource_line_relation,
                                  default.resource_area: self.resource_area_relation,
                                  default.report_point: self.report_point_relation,
                                  default.report_line: self.report_line_relation,
                                  default.report_area: self.report_area_relation}

        msg("Appending resource layers and table...")
        self.append(default.resource_lyrs,
                    "resourceid",
                    default.resources,
                    project.search_area)

        msg("Appending report layers and table...")
        self.append(default.report_lyrs,
                    "reportid",
                    default.reports,
                    project.search_area)

        self.resource_point = self.check_exists(self.resource_point)
        self.resource_line = self.check_exists(self.resource_line)
        self.resource_area = self.check_exists(self.resource_area)
        
        self.report_point = self.check_exists(self.report_point)
        self.report_line = self.check_exists(self.report_line)
        self.report_area = self.check_exists(self.report_area)
    
    def set_gdb(self, project):
        project_fld = os.path.dirname(os.path.dirname(project.gdb))
        output_fld = os.path.join(project_fld, "products")
        if not os.path.exists(output_fld):
            os.mkdir(output_fld)
        template = 'extract.gdb'
        gdb = os.path.join(output_fld, 'extract.gdb')
        shutil.copytree(template, gdb)
        return gdb

    def set_layer(self, name, record):
        ds = {"resource": self.resource_ds,
              "report": self.report_ds}[record]
        return os.path.join(ds, name)

    def set_relation(self, record, name):
        return os.path.join(self.gdb, "{0}_{0}{1}".format(record, name))

    def append(self, lyrs, uid, table, search_area):
        rec_bool = False
        rec_ids = set()
        rec_table = {"resourceid": self.resources,
                     "reportid": self.reports}[uid]
        
        for lyr in lyrs:
            arcpy.MakeFeatureLayer_management(lyr, "lyr")
            arcpy.SelectLayerByLocation_management("lyr",
                                                   "INTERSECT",
                                                   search_area,
                                                   "",
                                                   "NEW_SELECTION",
                                                   "NOT_INVERT")
            rec_lyr = self.rec_lyr_dict[lyr]
            rec_relation = self.rec_relation_dict[lyr]
            if not int(arcpy.GetCount_management("lyr").getOutput(0)) == 0:
                rec_bool = True
                with arcpy.da.SearchCursor("lyr", uid) as cursor:
                    rec_ids.update([row[0] for row in cursor])
                arcpy.Append_management("lyr", rec_lyr, "TEST")
            else:
                arcpy.Delete_management(rec_lyr)
                arcpy.Delete_management(rec_relation)

        if rec_bool:
            arcpy.MakeTableView_management(table, "table")
            rec_arg = ",".join([str(x) for x in rec_ids if x is not None])
            rec_exp = """{} IN ({})""".format(afd("table", uid), rec_arg)
            arcpy.SelectLayerByAttribute_management("table", "NEW_SELECTION", rec_exp)
            arcpy.Append_management("table", rec_table, 'NO_TEST')

            uid_lst = [row[0] for row in arcpy.da.SearchCursor("table", uid)]
            rep_arg = ",".join([str(x) for x in uid_lst if x is not None])

            i = 0
            with arcpy.da.UpdateCursor(rec_table, 'u' + uid) as cursor:
                for row in cursor:
                    row[0] = uid_lst[i]
                    cursor.updateRow(row)
                    i += 1

        else:
            msg("   No records found".format(os.path.basename(table)))

    def check_exists(self, lyr):
        if arcpy.Exists(lyr):
            return lyr
        else:
            return None
        
