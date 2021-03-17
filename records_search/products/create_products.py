# import modules
import arcpy, os, shutil
import pandas as pd

# import functions
from create_kmz import ExtractToKML
from export_tables import ExportTables
from extract_pdfs import ExtractPDFs
from export_shapefiles import ExportShapefiles
from send_edits import SendEdits

def create_products(gdb, kmz_bool, pdf_bool, shp_bool):

    # copy edits to global file
    # SendEdits(gdb)

    # set output directory
    out_dir = os.path.dirname(gdb)

    # define function inputs based on parameters
    site_tbl = os.path.join(gdb, "resources")
    rep_tbl = os.path.join(gdb, "reports")
    out_kmz = os.path.join(out_dir, "extract.kmz")
    out_site_xls = os.path.join(out_dir, "resources.xls")
    out_rep_xls = os.path.join(out_dir, "reports.xls")

    # export geodatabase extract to KMZ
    if kmz_bool:
        arcpy.AddMessage("Converting extract to KMZ...")
        ExtractToKML(gdb, out_kmz)
        arcpy.AddMessage("Done!")

    # convert tables to single XLSX
    arcpy.AddMessage("Converting tables to excel file...")
    ExportTables(site_tbl, rep_tbl, out_site_xls, out_rep_xls)
    arcpy.AddMessage("Done!")

    # copy PDFs of resources and reports
    if pdf_bool:
        arcpy.AddMessage("Copying PDFs from extract...")
        ExtractPDFs(gdb, out_dir)
        arcpy.AddMessage("Done!")

    # export shapefiles of feature classes
    if shp_bool:
        arcpy.AddMessage("Converting feature classes to shapefiles...")
        ExportShapefiles(gdb, out_dir)
        arcpy.AddMessage("Done!")

    arcpy.AddMessage("All products complete!")

