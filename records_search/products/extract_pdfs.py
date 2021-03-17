import arcpy, os, shutil

def ExtractPDFs(db, destDir):
    
    try:

        # create some new directories for our pdfs
        arcpy.AddMessage("   Creating directories...")
        dirPDF = os.path.join(destDir, "PDFs")
        if not os.path.isdir(dirPDF):
            os.mkdir(dirPDF)
        dirReps = os.path.join(destDir, "PDFs", "Reports")
        if not os.path.isdir(dirReps):
            os.mkdir(dirReps)
        dirSites = os.path.join(destDir,"PDFs","Site Records")
        if not os.path.isdir(dirSites):
            os.mkdir(dirSites)

        # a function for making county subdirectories
        def make_subdir(county):
            dir_cnty = os.path.join(destDir, "PDFs", "Site Records", county)
            if not os.path.isdir(dir_cnty):
                os.mkdir(dir_cnty)
        
        # move the site PDFs
        bad_resources = []
        
        arcpy.AddMessage("   Moving resource pdfs:")
        site_tbl = os.path.join(db, "resources")
        if arcpy.Exists(site_tbl):
            county_list = []
            with arcpy.da.SearchCursor(site_tbl, "pdf", "pdf is not null") as rows:
                for row in rows:
                    path = row[0].replace("old/", "new/")
                    if os.path.exists(path):
                        file_name = os.path.basename(path)
                        arcpy.AddMessage("     " + file_name)
                        sub_dir = os.path.basename(os.path.dirname(path))
                        if sub_dir not in county_list:
                            make_subdir(sub_dir)
                            county_list.append(sub_dir)
                        new_path = os.path.join(destDir, "PDFs", "Site Records", sub_dir, file_name)
                        if os.path.exists(new_path) == False:
                            shutil.copy(path, new_path)
                    else:
                        bad_resources.append(path)
        
        # move the report pdfs
        bad_reports = []
        
        arcpy.AddMessage("   Moving report pdfs:")
        rep_tbl = os.path.join(db, "reports")
        if arcpy.Exists(rep_tbl):
            with arcpy.da.SearchCursor(rep_tbl, "pdf", "pdf is not null") as rows:
                for row in rows:
                    path = row[0].replace("old/", "new/")
                    if os.path.exists(path):
                        file_name = os.path.basename(path)
                        arcpy.AddMessage("     " + file_name)
                        new_path = os.path.join(destDir, "PDFs", "Reports", file_name)
                        if os.path.exists(new_path) == False:
                            shutil.copy(path, new_path)
                    else:
                        bad_reports.append(path)

        # output a list of resources and reports with invalid paths
        if bad_resources:
            arcpy.AddMessage("  The following resource paths do not exist:")
            for path in bad_resources:
                arcpy.AddMessage("      " + path)
        
        if bad_reports:
            arcpy.AddMessage("  The following report paths do not exist:")
            for path in bad_reports:
                arcpy.AddMessage("      " + path)

    except Exception as e:
        arcpy.AddWarning(e.message)
