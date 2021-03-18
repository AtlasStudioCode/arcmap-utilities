from .general import *

from selenium import webdriver
from selenium.webdriver.common.by import By

import os, re, shutil, time
import pandas as pd

def download_files(row_id, driver):
    # download all files for a given row into the taskfreak download folder
    if type(row_id) == int:
        row_id = str(row_id)
    
    driver.find_element(By.XPATH, "//td[@id='etitl{0}']/a".format(row_id)).click()

    time.sleep(2)

    file_links = driver.find_elements(By.XPATH, "//table[@id='vfile']/tbody/tr")
    file_links = file_links[1:-1]

    for link in file_links:
        link.find_element(By.TAG_NAME, 'a').click()
        time.sleep(2)

    driver.find_element(By.LINK_TEXT, 'close').click()

def clean_name(project, title):
    # return a project name with project number at the end and special characters removed
    title = title.replace('_', ' ').replace('.', '').replace(',', '').replace('/', ' ').replace('\\', ' ').replace('#', ' ')

    num_exp = re.compile('[0-9]{7,9}')
    title_num = re.findall(num_exp, title)
    project_num = re.findall(num_exp, project)
    
    if len(title_num) == 1:
        title = title.replace(title_num[0], '') + ' ' + title_num[0]
    elif len(project_num) == 1:
        title = title + ' ' + project_num[0]

    title = title.strip()

    return title

def init_project_fld(project, title):
    # move downloaded files to a folder with the clean project name
    title = clean_name(project, title)
    project_fld = os.path.join(incoming_fld, title)

    if not os.path.exists(project_fld):
        os.mkdir(project_fld)

    time.sleep(5)

    for name in os.listdir(download_fld):
        home = os.path.join(download_fld, name)
        output = os.path.join(project_fld, name)
        shutil.move(home, output)

    return title

def empty_downloads():
    # empty the downloads folder
    for name in os.listdir(download_fld):
        home = os.path.join(download_fld, name)
        os.remove(home)

def mark_done(row_id, driver):
    # mark the row as downloaded in TaskFreak
    driver.find_element(By.ID, 'est1{0}'.format(row_id)).click()
    driver.switch_to_alert().dismiss()

def extract_rows(index, driver):
    # execute all functions for a range of rows and output a csv of project names and deadlines
    df = pd.DataFrame(columns = ['project_name'])
    
    for i in index:
        project, title = get_fields(i, driver)
        
        try:
            download_files(i, driver)
            title = init_project_fld(project, title)
            df = df.append({'project_name': title},
                           ignore_index = True)
            mark_done(i, driver)
        except Exception as e:
            print(e)
            empty_downloads()

    driver.quit()
    
    output_csv = 'imports.csv'
    df.to_csv(output_csv, index = False)
