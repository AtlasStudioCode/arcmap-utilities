import arcpy, os, shutil

from arcpy import AddMessage as msg

class Project:
    def __init__(self, work_loc = None, linear_unit = None, search_area = None):
        msg("Creating project geodatabase...")
        self.resource_fcs = self.set_record_fcs("Resource")
        self.report_fcs = self.set_record_fcs("Report")
        self.gdb = self.set_gdb(work_loc, search_area)
        self.work_loc = self.set_work_loc(work_loc)
        self.linear_unit = linear_unit
        self.search_area = self.set_search_area(search_area)

    def set_record_fcs(self, ds_name):
        default_sde = "default_sde"
        return [os.path.join(default_sde,
                             "pgelibrary.geo." + ds_name,
                             "pgelibrary.geo." + ds_name + fc_name)
                for fc_name in ["Point", "Line", "Area"]]

    def set_gdb(self, work_loc, search_area):
        if work_loc:
            gis = work_loc
        elif search_area:
            gis = search_area
        temp = os.path.dirname(gis)
        while not os.path.basename(temp) == "client":
            temp = os.path.dirname(temp)
        query_folder = os.path.dirname(temp)
        data_folder = os.path.join(query_folder, "data")
        if not os.path.exists(data_folder):
            os.mkdir(data_folder)
        gdb = os.path.join(data_folder, "project.gdb")
        if os.path.exists(gdb):
            shutil.rmtree(gdb)
        arcpy.CreateFileGDB_management(data_folder, "project.gdb")
        return gdb

    def set_work_loc(self, work_loc):
        if work_loc:
            shape_type = arcpy.Describe(work_loc).shapeType
            suffix = {"Point": "point",
                      "Polyline": "line",
                      "Polygon": "area"}[shape_type]
            work_loc_name = "work_" + suffix
            path = os.path.join(self.gdb, work_loc_name)
            arcpy.CopyFeatures_management(work_loc, path)
            return path
        else:
            return None
    
    def set_search_area(self, search_area):
        if search_area:
            path = os.path.join(self.gdb, "search_area")
            arcpy.CopyFeatures_management(search_area, path)
            return path    
        else:
            path = os.path.join(self.gdb, "search_area")
            arcpy.Buffer_analysis(self.work_loc, path, self.linear_unit,
                                  "FULL", "ROUND", "ALL", "", "PLANAR")
            return path
        
