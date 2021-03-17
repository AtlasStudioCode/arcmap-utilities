from extract_data_defs import *

driver = webdriver.Firefox(profile)

login('username', 'password', download_page, driver)

proj_lst = get_projects(find_new_rows(driver), driver)

set_creds(proj_lst, cred_page, driver)

print('Done')
input()
