import os

# set folders list within the current working directory and filter list
folders = os.listdir(os.getcwd())
folders = [folder for folder in folders if '.' not in folder]

def rename(fld):
    # change the names of the gis folder and pdf files to match the parent folder
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
    # perform a rename for each folder in the folder list
    rename(folder)

# keep terminal window open until user gives input
input()
