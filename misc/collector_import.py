import arcpy, os, datetime
from arcpy import AddMessage as msg

# get input database and export database from script parameters
input_db = arcpy.GetParameterAsText(0)
export_db = arcpy.GetParameterAsText(1)

# get input database name
datafile = os.path.basename(input_db)

# dict to relate input fc to output fc
lyr_key = {'GPS_Non_resource__Area_': 'nresarea',
           'GPS_Non_resource__Line_': 'nresline',
           'GPS_Non_resource__Point_': 'nrespoint',
           'GPS_Resource__Area_': 'resarea',
           'GPS_Resource__Line_': 'resline',
           'GPS_Resource__Point_': 'respoint'}

def fix_proj(lyr):
    # define projection as WGS84 if undefined
    shp_desc = arcpy.Describe(lyr)
    if shp_desc.spatialReference.name == 'Unknown':
        arcpy.DefineProjection_management(lyr, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
    arcpy.RepairGeometry_management(lyr, "KEEP_NULL")
    return lyr

def get_rcvr(lyr):
    # find rcvr for point data
    field_names = [field.name for field in arcpy.ListFields(lyr)]
    if 'ESRIGNSS_RECEIVER' in field_names:
        rcvr_lst = [row[0] for row in arcpy.da.SearchCursor(lyr, 'ESRIGNSS_RECEIVER', 'ESRIGNSS_RECEIVER IS NOT NULL')]
                                                            
    if 'rcvr_type' in field_names:
        rcvr_lst = [row[0] for row in arcpy.da.SearchCursor(lyr, 'rcvr_type', 'rcvr_type IS NOT NULL')]

    rcvr_lst = list(set(rcvr_lst))
    if len(rcvr_lst) == 0:
        return 'Collector'
    elif len(rcvr_lst) == 1:
        return rcvr_lst[0]
    else:
        raise ValueError('ERROR: There are two different reciever types.')

def fix_fields(lyr):
    # change field names to match export database
    field_names = [field.name for field in arcpy.ListFields(lyr)]
    
    lyr_name = arcpy.Describe(lyr).baseName
    if lyr_name in ('GPS_Non_resource__Point_', 'GPS_Resource__Point_') and 'rcvr_type' not in field_names:
        arcpy.AlterField_management(lyr, 'ESRIGNSS_RECEIVER', 'rcvr_type')

def add_fields(lyr, rcvr):
    # add fields to match export database
    field_names = [field.name for field in arcpy.ListFields(lyr)]
    
    if 'rcvr_type' not in field_names:
        arcpy.AddField_management(lyr, 'rcvr_type', 'TEXT', field_length = 20)
    rcvr_arg = '\"' + rcvr + '\"'
    arcpy.CalculateField_management(lyr, 'rcvr_type', rcvr_arg, 'PYTHON')

    if 'source' not in field_names:
        arcpy.AddField_management(lyr, 'source', 'TEXT', field_length = 20)
    arcpy.CalculateField_management(lyr, 'source', '"GPS"', 'PYTHON')

    if 'datafile' not in field_names:
        arcpy.AddField_management(lyr, 'datafile', 'TEXT', field_length = 40)
    datafile_arg = '\"' + datafile + '\"'
    arcpy.CalculateField_management(lyr, 'datafile', datafile_arg, 'PYTHON')

    lyr_name = arcpy.Describe(lyr).baseName
    if lyr_name in ('GPS_Non_resource__Point_', 'GPS_Resource__Point_'):
        
        if 'gps_time' not in field_names:
            arcpy.AddField_management(lyr, 'gps_time', 'TEXT', field_length = 20)
        time_exp = 'get_time(!ESRIGNSS_FIXDATETIME!)'
        time_code = """def get_time(old_fld):
            time = old_fld.split(' ')[1] + old_fld.split(' ')[2].lower()
            return time"""
        arcpy.CalculateField_management(lyr, 'gps_time', time_exp, 'PYTHON', time_code)

        if 'gps_date' not in field_names:
            arcpy.AddField_management(lyr, 'gps_date', 'TEXT', field_length = 20)
        date_exp = 'get_date(!ESRIGNSS_FIXDATETIME!)'
        date_code = """def get_date(old_fld):
            date = old_fld.split(' ')[0]
            return date"""
        arcpy.CalculateField_management(lyr, 'gps_date', date_exp, 'PYTHON', date_code)

def append_data(lyr):
    # append cleaned import data to export database
    lyr_name = arcpy.Describe(lyr).baseName
    out_lyr_name = lyr_key[lyr_name]
    out_lyr_path = os.path.join(export_db, 'Resources', out_lyr_name)

    arcpy.Append_management(lyr, out_lyr_path, 'NO_TEST')

try:

    # set working env to input database
    arcpy.env.workspace = input_db

    # get list of input fc that start with 'GPS'
    input_lyrs = arcpy.ListFeatureClasses('GPS*')

    # find rcvr for import data
    rcvr1 = get_rcvr('GPS_Non_resource__Point_')
    rcvr2 = get_rcvr('GPS_Resource__Point_')
    
    if rcvr1 == 'Collector' and rcvr2 == 'Collector':
        rcvr = 'Collector'
    elif rcvr1 == 'Collector':
        rcvr = rcvr2
    elif rcvr2 == 'Collector':
        rcvr = rcvr1
    elif rcvr1 == rcvr2:
        rcvr = rcvr1
    else:
        raise ValueError('ERROR: There are two different reciever types.')
    
    # run functions for each fc
    for input_lyr in input_lyrs:
        lyr_name = arcpy.Describe(input_lyr).baseName
        msg('   Transferring data from ' + '\"' + lyr_name + '\"...')
        
        fix_lyr = fix_proj(input_lyr)
        fix_fields(fix_lyr)
        add_fields(fix_lyr, rcvr)
        append_data(fix_lyr)

except Exception as e:
    arcpy.AddError('   ' + e.message)
    

