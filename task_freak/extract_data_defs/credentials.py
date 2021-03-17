from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

def set_cred(proj_num, page, driver):
    # set individual credentials for a given project name

    driver.get(page)
        
    elems = driver.find_elements(By.LINK_TEXT, proj_num)

    for i in range(len(elems)):
        try:
            print("Setting credentials for project " + proj_num + "...")
            driver.get(page)
            
            elem = driver.find_elements(By.LINK_TEXT, proj_num)[i]

            elem.click()

            driver.find_element(By.LINK_TEXT, "Add a user to this project").click()

            Select(driver.find_element(By.NAME, "nuser")).select_by_value("70")
            Select(driver.find_element(By.NAME, "nposition")).select_by_value("5")

            driver.find_element(By.NAME, "invite").click()

            print("Success!\n")

        except Exception as e:
            print(e)
    
def set_creds(project_lst, page, driver):
    # set credentials for a list of project names
    for project in project_lst:
        set_cred(project, page, driver)
    driver.quit()
