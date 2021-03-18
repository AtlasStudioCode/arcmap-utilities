import os
import numpy as np
import pandas as pd

# read projects csv as a pandas dataframe
prj = pd.read_csv('projects.csv')

def get_root(path):
    # get the root of the given path
    head, tail = os.path.split(path)
    return head

def make_path(row):
    # utility function to create a new folder path to the clean project name
    return os.path.join(get_root(row['PathCopy']), row['CleanProjectName'])

def make_pdf_path(row):
    # create path for new project pdf file in clean folder
    pdf_file = row['CleanProjectName'] + '.pdf'
    return os.path.join(row['newPath'], pdf_file)

def check_pdf(row):
    # print the name, region, and forest of a project where pdf file does not exist
    if not os.path.exists(row['origPDF']):
        print(row['CleanProjectName'])
        print(row['Sub'])
        print(row['Forest'])
        print('')

# create new columns in the dataframe
prj['newPath'] = prj.apply(make_path, axis = 1)
prj['origPDF'] = prj.apply(make_pdf_path, axis = 1)

# output a csv with these new columns from the dataframe
prj.to_csv('projects_new.csv')

# apply the check_pdf function to each row of the dataframe
prj.apply(check_pdf, axis = 1)