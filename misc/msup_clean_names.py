import os
import numpy as np
import pandas as pd

prj = pd.read_csv('projects.csv')

def get_root(path):
    head, tail = os.path.split(path)
    return head

def make_path(row):
    return os.path.join(get_root(row['PathCopy']), row['CleanProjectName'])

prj['newPath'] = prj.apply(make_path, axis = 1)

def make_pdf_path(row):
    pdf_file = row['CleanProjectName'] + '.pdf'
    return os.path.join(row['newPath'], pdf_file)

prj['origPDF'] = prj.apply(make_pdf_path, axis = 1)

prj.to_csv('projects_new.csv')

def check_pdf(row):
    if not os.path.exists(row['origPDF']):
        print(row['CleanProjectName'])
        print(row['Sub'])
        print(row['Forest'])
        print('')

prj.apply(check_pdf, axis = 1)

