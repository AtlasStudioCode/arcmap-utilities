import arcpy, os

kmz = arcpy.GetParameterAsText(0)
folder = os.path.dirname(kmz)

arcpy.AddMessage('  Converting KMZ to geodatabase...')

arcpy.KMLToLayer_conversion(kmz, folder, 'temp')
