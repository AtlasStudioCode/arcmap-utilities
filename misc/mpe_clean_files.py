import os

folders = os.listdir(os.getcwd())
folders = [folder for folder in folders if '.' not in folder]

def rename(fld):
    files = os.listdir(fld)
    if len([file for file in files if '.pdf' in file]) == 1 and len(files) < 3:
        gis = fld + ' GIS'
        rep = fld + '.pdf'
        for file in files:
            if '.pdf' in file:
                os.rename(os.path.join(fld, file), os.path.join(fld, rep))
            else:
                os.rename(os.path.join(fld, file), os.path.join(fld, gis))
    else:
        print(fld)

for folder in folders:
    rename(folder)


input()
