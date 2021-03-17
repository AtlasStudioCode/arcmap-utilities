import arcpy, os

from arcpy import AddMessage as msg
from arcpy import AddFieldDelimiters as afd

from mxd import Mxd

class Request(Mxd):
    def __init__(self, project, extract):
        Mxd.__init__(self)

        self.work_point = self.set_layer("Project Location")
        self.work_line = self.set_layer("Project Centerline")
        self.work_area = self.set_layer("Area of Potential Effects")
        self.work_lyrs = [self.work_point,
                          self.work_line,
                          self.work_area]
        self.search_area = self.set_layer("[] Records Search Extent")

        self.site = self.set_layer("Site")
        self.study = self.set_layer("Study")

        self.fc_dict = {self.resource_point: extract.resource_point,
                        self.resource_line: extract.resource_line,
                        self.resource_area: extract.resource_area,
                        self.report_point: extract.report_point,
                        self.report_line: extract.report_line,
                        self.report_area: extract.report_area}

        msg("Updating map document...")
        self.update_map(project, extract)

    def set_datasource(self, lyr, db, fc):
        lyr.replaceDataSource(db, "FILEGDB_WORKSPACE", fc, False)

    def remove_layer(self, lyr):
        arcpy.mapping.RemoveLayer(self.df, lyr)

    def update_map(self, project, extract):
        for lyr in self.work_lyrs:
            if project.work_loc:
                work_name = os.path.basename(project.work_loc)
                if work_name == lyr.datasetName:
                    self.set_datasource(lyr, project.gdb, work_name)
                else:
                    self.remove_layer(lyr)
            else:
                self.remove_layer(lyr)
        
        self.set_datasource(self.search_area, project.gdb, "search_area")
        num = project.linear_unit.split()[0]
        units = project.linear_unit.split()[1].lower()
        self.search_area.name = "{0}-{1} Records Search Extent".format(num, units)

        for lyr in self.resource_lyrs:
            fc = self.fc_dict[lyr]
            if fc:
                name = os.path.basename(fc)
                self.set_datasource(lyr, extract.gdb, name)
                if "Area" in lyr.name:
                    self.set_datasource(self.site, extract.gdb, name)
            else:
                self.remove_layer(lyr)
                if "Area" in lyr.name:
                    self.remove_layer(self.site)

        for lyr in self.report_lyrs:
            fc = self.fc_dict[lyr]
            if fc:
                name = os.path.basename(fc)
                self.set_datasource(lyr, extract.gdb, name)
                if "Area" in lyr.name:
                    self.set_datasource(self.study, extract.gdb, name)
            else:
                self.remove_layer(lyr)
                if "Area" in lyr.name:
                    self.remove_layer(self.study)

        arcpy.RefreshActiveView()