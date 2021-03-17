import arcpy, os

def ExtractToKML(db, outKMZpath):
    
    try:

        if os.path.exists(outKMZpath):
            return

        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = mxd.activeDataFrame

        # add an empty group layer
        arcpy.AddMessage("   Creating group layer...")
        arcpy.mapping.AddLayer(df, arcpy.mapping.Layer('group.lyr'))
        lyr_grp = arcpy.mapping.ListLayers(mxd, "Resources and Reports", df)[0]

        # get all the feature classes in the extract and then add them to the group layers
        """
        arcpy.AddMessage("   Adding feature classes:")
        arcpy.env.workspace = db
        fc_lst = []
        for ds in arcpy.ListDatasets():
            for fc in arcpy.ListFeatureClasses(feature_dataset = ds):
                temp_fc_name = arcpy.Describe(fc).name + "_select"
                temp_fc = arcpy.Select_analysis(fc, temp_fc_name)
                fld_lst = [f.name for f in arcpy.ListFields(temp_fc)]
                for badfield in ["origsiteid", "origreportid"]:
                    if badfield in fld_lst:
                        arcpy.DeleteField_management(temp_fc, badfield)
                #fc_lst.append([fc, arcpy.Describe(temp_fc).catalogPath])
                fc_lst.append(temp_fc_name)
        arcpy.AddMessage(fc_lst)
        """
        arcpy.env.workspace = db
        fc_lst = []
        
        for ds in arcpy.ListDatasets():
            for fc in arcpy.ListFeatureClasses(feature_dataset = ds):
                fc_lst.append(arcpy.Describe(fc).name)
        
        lyr_dict = {'Resource (Point)': 'ResourcePoint',
                    'Resource (Linear)': 'ResourceLine',
                    'Resource (Polygon)': 'ResourceArea',
                    'Study (Point)': 'ReportPoint',
                    'Study (Linear)': 'ReportLine',
                    'Study (Polygon)': 'ReportArea'}

        arcpy.AddMessage("   Replacing data sources...")
        for lyr in lyr_grp:
            arcpy.AddMessage(lyr.name)
            if lyr.name in lyr_dict:
                my_fc = lyr_dict[lyr.name]
                if my_fc in fc_lst:
                    lyr.replaceDataSource (db, "FILEGDB_WORKSPACE", my_fc, False)
                else:
                    #arcpy.AddMessage("Bad layer!")
                    arcpy.mapping.RemoveLayer(df, lyr)
                arcpy.RefreshActiveView()

        # create kml file
        arcpy.AddMessage("   Creating KMZ...")
        arcpy.LayerToKML_conversion(lyr_grp, outKMZpath)

        arcpy.AddMessage("The file " + outKMZpath + " has been created.")
        
        arcpy.mapping.RemoveLayer(df, lyr_grp)
        arcpy.RefreshActiveView()

    except Exception as e:
        arcpy.AddWarning(e.message)
        
    """
    for fc in fc_lst:
        if arcpy.Exists(fc):
            arcpy.Delete_management(fc)
    """
