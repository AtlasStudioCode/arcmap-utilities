import arcpy

from arcpy import AddFieldDelimiters as afd
from arcpy import AddMessage as msg

# get current map document
mxd = arcpy.mapping.MapDocument('CURRENT')

# get four tables in current map document
batch_tbl = arcpy.mapping.ListTableViews(mxd, 'pgelibrary.geo.batch')[0]
batch_resource_tbl = arcpy.mapping.ListTableViews(mxd, 'pgelibrary.geo.batchresource')[0]
resource_tbl = arcpy.mapping.ListTableViews(mxd, 'pgelibrary.geo.resources')[0]
relate_tbl = arcpy.mapping.ListTableViews(mxd, 'pgelibrary.geo.resourcereportevents')[0]

class primary:
    # class to represent a primary number resource
    def __init__(self, county, _id):
        self.county = county
        self.id = _id

class trinomial:
    # class to represent a trinomial number resource
    def __init__(self, county, _id):
        self.name = county
        self.county = self.decode(county)
        self.id = _id

    def decode(self, county):
        # change an int county code to a three letter string
        decode_lst = [''   , 'ALA', 'ALP', 'AMA', 'BUT',
                      'CAL', 'COL', 'CCO', 'DNO', 'ELD',
                      'FRE', 'GLE', 'HUM', 'IMP', 'INY',
                      'KER', 'KIN', 'LAK', 'LAS', 'LAN',
                      'MAD', 'MRN', 'MRP', 'MEN', 'MER',
                      'MOD', 'MNO', 'MNT', 'NAP', 'NEV',
                      'ORA', 'PLA', 'PLU', 'RIV', 'SAC',
                      'SBN', 'SBR', 'SDI', 'SFR', 'SJO',
                      'SLO', 'SMA', 'SBA', 'SCL', 'SCR',
                      'SHA', 'SIE', 'SIS', 'SOL', 'SON',
                      'STA', 'SUT', 'TEH', 'TRI', 'TUL',
                      'TUO', 'VEN', 'YOL', 'YUB']
        return decode_lst.index(county)

class forest:
    # class to represent a forest service number resource
    def __init__(self, f1, f2, f3, f4):
        self.f1 = f1
        self.f2 = f2
        self.f3 = f3
        self.f4 = f4

class other:
    # class to represent an other number resource
    def __init__(self, name):
        self.name = name

def get_name(code_type, v1, v2, v3, v4, name):
    # utility function to format a given resource code type
    name_dict = {'primary': """P-{}-{}""".format(v1, v2),
                 'trinomial': """CA-{}-{}""".format(name, v2),
                 'forest': """FS {}-{}-{}-{}""".format(v1, v2, v3, v4),
                 'other': """{}""".format(v1)}
    return name_dict[code_type]

def get_expr(code_type, f1, v1, f2, v2, f3, v3, f4, v4):
    # get the sql query to select a resource given the input codes
    f1 = afd(resource_tbl.dataSource, f1)
    if f2:
        f2 = afd(resource_tbl.dataSource, f2)
    if f3:
        f3 = afd(resource_tbl.dataSource, f3)
    if f4:
        f4 = afd(resource_tbl.dataSource, f4)
    expr_dict = {'primary': """{} = {} AND {} = {}""".format(f1, v1, f2, v2),
                 'trinomial': """{} = {} AND {} = {}""".format(f1, v1, f2, v2),
                 'forest': """{} = {} AND {} = {} AND {} = {} AND {} = {}""".format(f1, v1, f2, v2, f3, v3, f4, v4),
                 'other': """{} = '{}'""".format(f1, v1)}
    return expr_dict[code_type]

def append_relation(report_id, code_type, f1, v1, f2 = None, v2 = None, f3 = None, v3 = None, f4 = None, v4 = None, name = None):
    # add an entry into the relationship table for the input report and resource
    resource_name = get_name(code_type, v1, v2, v3, v4, name)
    expr = get_expr(code_type, f1, v1, f2, v2, f3, v3, f4, v4)

    with arcpy.da.SearchCursor(resource_tbl.dataSource, 'resourceid', expr) as cursor:
        resource_ids = [row[0] for row in cursor]

    if len(resource_ids) == 1:
        resource_id = resource_ids[0]

        edit = arcpy.da.Editor(relate_tbl.workspacePath)
        edit.startEditing(False, True)
        edit.startOperation()

        with arcpy.da.InsertCursor(relate_tbl.dataSource, ['reportid', 'resourceid']) as cursor:
            cursor.insertRow((report_id, resource_id))

        edit.stopOperation()
        edit.stopEditing(True)
        
        msg('\t{} related to report {}!'.format(resource_name, report_id))
        
    elif len(resource_ids) > 1:
        msg('\t{} has multiple matching resources.'.format(resource_name))
        
    else:
        msg('\t{} has zero matching resources.'.format(resource_name))

def get_batch_id(batch_name):
    # utility function to get the batch id for a given batch name
    expr = """{} = '{}'""".format(afd(batch_tbl.dataSource, 'batchname'), batch_name)
    with arcpy.da.SearchCursor(batch_tbl.dataSource, 'globalid', expr) as cursor:
        batch_ids = [row[0] for row in cursor]
        if len(batch_ids) == 1:
            return batch_ids[0]
        elif len(batch_ids) == 0:
            raise Exception("Batch name does not exist.")
        else:
            raise Exception("Batch name resulted in unknown error.")

def append_to_batch(batch_name, code_type, f1, v1, f2 = None, v2 = None, f3 = None, v3 = None, f4 = None, v4 = None, name = None):
    # add an entry into the batch resource table for the input resource
    batch_id = get_batch_id(batch_name)
    resource_name = get_name(code_type, v1, v2, v3, v4, name)
    expr = get_expr(code_type, f1, v1, f2, v2, f3, v3, f4, v4)

    with arcpy.da.SearchCursor(resource_tbl.dataSource, 'resourceid', expr) as cursor:
        resource_ids = [row[0] for row in cursor]

    if len(resource_ids) > 0:
        for resource_id in resource_ids:
            edit = arcpy.da.Editor(batch_resource_tbl.workspacePath)
            edit.startEditing(False, True)
            edit.startOperation()

            with arcpy.da.InsertCursor(batch_resource_tbl.dataSource, ['batchid', 'resourceid']) as cursor:
                cursor.insertRow((batch_id, resource_id))

            edit.stopOperation()
            edit.stopEditing(True)
            
            msg('\t{} added to batch!'.format(resource_name))
        
    else:
        msg('\t{} has zero matching resources.'.format(resource_name))
