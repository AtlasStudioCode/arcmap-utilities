import arcpy, os

arcpy.ImportToolbox('tools.tbx', 'tools')

mxd = arcpy.mapping.MapDocument("CURRENT")
df = mxd.activeDataFrame

project_gdb = arcpy.GetParameterAsText(0)

arcpy.env.workspace = project_gdb

arcpy.AddMessage('  Generating viewport grid...')

arcpy.GridIndexFeatures_cartography('viewports',
                                    'search_area',
                                    use_page_unit = True,
                                    scale = 24000,
                                    label_from_origin = True)

viewport_lyr = arcpy.mapping.ListLayers(mxd, 'Viewports', df)[0]
viewport_lyr.replaceDataSource(project_gdb, "FILEGDB_WORKSPACE", 'viewports', False)

arcpy.AddMessage('  Adding record search fields to viewport layer...')

arcpy.RecordSearchFields2_farwestern(viewport_lyr, 'PLSS Main', False, False, 'Pretty string')



