import arcpy, os

def ExportShapefiles(gdb, out_dir):
    # export shapefiles for all feature classes in the input geodatabase
    try:
        out_shp_fld = os.path.join(out_dir, 'shapefiles')
        
        if os.path.exists(out_shp_fld):
            return
        else:
            os.mkdir(out_shp_fld)

        arcpy.env.workspace = gdb

        input_feat = []
        
        for ds in arcpy.ListDatasets():
            for fc in arcpy.ListFeatureClasses(feature_dataset = ds):
                input_feat.append(os.path.join(ds, fc))

        arcpy.FeatureClassToShapefile_conversion(input_feat, out_shp_fld)

    except Exception as e:
        arcpy.AddWarning(e.message)
