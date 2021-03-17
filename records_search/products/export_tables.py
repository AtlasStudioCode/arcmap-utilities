import arcpy, os
import pandas as pd
import openpyxl as xl
from openpyxl.cell.cell import WriteOnlyCell
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.datavalidation import DataValidation

def ExportTables(site_tbl, rep_tbl, out_site_xls, out_rep_xls):

    # define output directory and output XLSX path
    out_dir = os.path.dirname(out_site_xls)
    out_xlsx = os.path.join(out_dir, "Resources and Reports.xlsx")

    # end function if XLSX already exists
    if os.path.exists(out_xlsx):
        return

    # convert geodatabase tables to XLS files
    arcpy.TableToExcel_conversion(site_tbl, out_site_xls, "NAME", "CODE")
    arcpy.TableToExcel_conversion(rep_tbl, out_rep_xls, "NAME", "CODE")

    # import xls files as dataframes
    site_df = pd.read_excel(out_site_xls, index_col = 0)
    rep_df = pd.read_excel(out_rep_xls, index_col = 0)

    # create output workbook with resource and report worksheets
    out_wb = xl.load_workbook("tables_temp.xlsx")
    site_ws = out_wb['Resources']
    rep_ws = out_wb['Reports']

    # convert dataframes to worksheets
    def dataframe_to_worksheet(df, ws):
        rows = dataframe_to_rows(df, index=False, header=False)
        for rid, row in enumerate(rows, 2):
            for cid, val in enumerate(row, 1):
                ws.cell(rid, cid, val)

    dataframe_to_worksheet(site_df, site_ws)
    dataframe_to_worksheet(rep_df, rep_ws)
    
    # save final xlsx
    out_wb.save(out_xlsx)

    # remove old XLS files
    os.remove(out_site_xls)
    os.remove(out_rep_xls)

    

    

    
