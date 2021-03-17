from selenium import webdriver
from selenium.webdriver.common.by import By

profile = "profile"

download_page = "download_page.com"
cred_page = "credentials_page.com"
task_page = "task_page.com"

download_fld = "download_folder/"
incoming_fld = "incoming_folder/"
output_csv = "imports.csv"

def login(username, password, page, driver):
    # login to task freak with username and password
    try:
        driver.get(page)

        print("Logging in...")
        driver.find_element(By.NAME, 'username').send_keys(username)
        driver.find_element(By.NAME, 'password').send_keys(password)
        driver.find_element(By.NAME, 'login').click()
        print("Success!\n")
        
    except Exception as e:
        print("No login needed.\n")
              
def get_fields(row_id, driver):
    # return project and title for a given row id
        if type(row_id) == int:
            row_id = str(row_id)
        
        project = driver.find_element(By.ID, 'eproj{}'.format(row_id)).text
        title = driver.find_element(By.ID, 'etitl{}'.format(row_id)).text
        
        return project, title

def find_all_rows(driver):
    # returns a list of all row ids
    rows = driver.find_elements(By.XPATH, "//table[@id='taskSheet']/tbody/tr")
    all_row_ids = []
    
    for row in rows:
        row_id = row.get_attribute('id')
        all_row_ids.append(row_id)

    return all_row_ids

def find_new_rows(driver):
    # returns a list of row ids that are marked as incomplete
    rows = driver.find_elements(By.XPATH, "//table[@id='taskSheet']/tbody/tr")
    new_row_ids = []
    
    for row in rows:
        row_id = row.get_attribute('id')
        status = row.find_element(By.ID, 'est1{}'.format(row_id)).get_attribute('class')

        if status == 'sts0':
            new_row_ids.append(row_id)

    return new_row_ids

def get_projects(index, driver):
    #
    project_lst = []

    for i in index:

        try:
            project, title = get_fields(i, driver)
            project_lst.append(project)

        except Exception as e:
            print(e)

    return list(set(project_lst))
