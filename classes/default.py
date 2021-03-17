import arcpy, os

class Default:
    def __init__(self):
        self.sde = 'sde_path'
        
        self.resource_ds = os.path.join(self.sde, "pgelibrary.geo.Resource")
        self.report_ds = os.path.join(self.sde, "pgelibrary.geo.Report")
        
        self.resources = os.path.join(self.sde, "pgelibrary.geo.resources")
        self.reports = os.path.join(self.sde, "pgelibrary.geo.reports")

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
    
    def set_layer(self, name, record_type):
        ds = {"resource": self.resource_ds,
              "report": self.report_ds}[record_type]
        return os.path.join(ds, "pgelibrary.geo." + name)
