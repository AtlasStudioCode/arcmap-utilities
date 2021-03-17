from extract_data_defs import *

driver = webdriver.Firefox(profile) 

login("username", "password", task_page, driver)

import_csv = 'U:/scripts/task_freak/imports.csv'
make_tasks(import_csv, task_page, driver)

print('Done')
input()

