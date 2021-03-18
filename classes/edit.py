import arcpy, os
import pandas as pd

from mxd import Mxd

class Edit(Mxd):
    # class to represent an edit session of a given map document class object
    def __init__(self):
        # initialize the edit class properties
        Mxd.__init__(self)
        self.raster_group = self.set_layer("Rasters")
        
    def append(self, gis, num):
        # append shapefiles to geodatabase feature classes and add georeferenced images to map if present
        if not pd.isnull(gis):
            
            if gis.endswith(".tiff") or gis.endswith(".jpg"):
                raster = arcpy.MakeRasterLayer_management(gis, num).getOutput(0)
                arcpy.mapping.AddLayerToGroup(self.df, self.raster_group, raster, "BOTTOM")
    
            elif os.path.isdir(gis):
                shps = [os.path.join(gis, f) for f in os.listdir(gis) if f.endswith(".shp")]
                for shp in shps:
                    file_name = os.path.basename(shp)

                    if len(arcpy.ListFields(shp, "feattype")) == 1:
                        arcpy.DeleteField_management(shp, "feattype")
                    if len(arcpy.ListFields(shp, "comment")) == 1:
                        arcpy.DeleteField_management(shp, "comment")
                    if len(arcpy.ListFields(shp, "uid")) == 0:
                        arcpy.AddField_management(shp, "uid", "LONG")
                    if len(arcpy.ListFields(shp, "file_name")) == 0:
                        arcpy.AddField_management(shp, "file_name", "TEXT")
                    
                    with arcpy.da.UpdateCursor(shp, ["file_name", "uid"]) as cursor:
                        for row in cursor:
                            row[0] = file_name[:50]
                            row[1] = num
                            cursor.updateRow(row)
                    
                    shape = arcpy.Describe(shp).shapeType
                    lyr = {"Point": self.report_point,
                           "Multipoint": self.report_point,
                           "Polyline": self.report_line,
                           "Polygon": self.report_area}[shape]
                    arcpy.Append_management(shp, lyr, "NO_TEST")
