import arcpy, os

class Mxd:
    # class to represent a map document
    def __init__(self):
        # initialize the mxd class properties
        self.doc = arcpy.mapping.MapDocument("CURRENT")
        self.df = self.doc.activeDataFrame

        self.resources = self.set_table("resources")
        self.reports = self.set_table("reports")

        self.resource_point = self.set_layer("ResourcePoint")
        self.resource_line = self.set_layer("ResourceLine")
        self.resource_area = self.set_layer("ResourceArea")
        self.resource_lyrs = [self.resource_point,
                              self.resource_line,
                              self.resource_area]
        
        self.report_point = self.set_layer("ReportPoint")
        self.report_line = self.set_layer("ReportLine")
        self.report_area = self.set_layer("ReportArea")
        self.report_lyrs = [self.report_point,
                            self.report_line,
                            self.report_area]

    def set_table(self, name):
        # utility function to create a table view object from a given table
        if len(arcpy.mapping.ListTableViews(self.doc, "pgelibrary.geo." + name)) > 0:
            return arcpy.mapping.ListTableViews(self.doc, "pgelibrary.geo." + name)[0]
        else:
            return None

    def set_layer(self, name):
        # utility function to create a layer from a given feature class
        if len(arcpy.mapping.ListLayers(self.doc, name)) > 0:
            return arcpy.mapping.ListLayers(self.doc, name)[0]
        else:
            return None
