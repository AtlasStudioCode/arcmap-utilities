from extract_data_defs import *

driver = webdriver.Firefox(profile)

login('username', 'password', download_page, driver)

driver.get(download_page)
index = find_new_rows(driver)
print('New rows found: {}\n'.format(len(index)))

extract_rows(index, driver)

driver.get(download_page)
index = find_new_rows(driver)
print('New rows remaining: {}\n'.format(len(index)))

print('Done')
input()
