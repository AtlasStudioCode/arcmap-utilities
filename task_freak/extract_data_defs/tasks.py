from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import os
from datetime import *
import pandas as pd

def new_task(page, driver):
    #
    driver.get(page)
    
    driver.find_element(By.XPATH, "//input[@value='new task']").click()

def set_name(name, driver):
    #
    driver.find_element(By.NAME, 'task_name').send_keys(name)

def set_date(driver):
    #    
    driver.find_element(By.LINK_TEXT, 'Dates').click()

    driver.find_element(By.XPATH, "//input[@value='Finish Date']").click()

def save_task(driver):
    #
    driver.find_element(By.NAME, 'btnFuseAction2').click()

def make_task(name, page, driver):
    #
    new_task(page, driver)
    set_name(name, driver)
    set_date(driver)
    save_task(driver)

def check_exist(lst, driver):
    #
    page = 'task_page'
    driver.get(page)
    
    new_lst = []

    for item in lst:
        try:
            driver.find_element(By.LINK_TEXT, item)
        except:
            new_lst.append(item)

    return new_lst
            

def make_tasks(import_csv, page, driver):
    #
    df = pd.read_csv(import_csv)
    projs = df.project_name.tolist()

    new_projs = check_exist(projs, driver)
    print('Adding {} new tasks...'.format(len(new_projs)))

    bad_projs = []

    for proj in new_projs:
        try:
            make_task(proj, page, driver)

        except Exception as e:
            print('[{}]: {}'.format(proj, e))
            bad_projs.append(proj)

    print('The following tasks were not added:')
    for proj in bad_projs:
        print(' {}'.format(proj))

    driver.quit()
    
