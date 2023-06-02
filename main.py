import contextlib

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

from utils import *


# TODO:
# Add WITHOUT_SUBMIT flag
# Replace all popup closes with close_annoying_popup(driver)
# Refactor to take arguments from command line using argparse

# Dev Flags
DRY_RUN = False
SKIP_SUBMIT = False

ONE_MONTH = True
RESUME = True
START_MONTH = "June-2022"
START_DISTRICT = "AGRA"

# if LOOP_ONCE is true then district is taken from this const
DISTRICT_IN_DATA = "ALIGARH -[AL]"

EXCEL_FILE = "MIS_ASHA.xlsx"
LOGIN_URL = "https://164.100.58.239/Report/mobileverify"
SCHEME_NAME = "ASHA Incentives"
STATE = "Uttar Pradesh"
FINANCIAL_YEAR = "2022-2023"
SCHEME_MONTHS = [
    "April-2022",
    "May-2022",
    "June-2022",
    "July-2022",
    "August-2022",
    "September-2022",
    "October-2022",
    "November-2022",
    "December-2022",
    "January-2023",
    "February-2023",
    "March-2023",
]
DISTRICTS = [
    "AGRA",
    "ALIGARH",
    "AMBEDKAR NAGAR",
    "Amethi",
    "AMROHA",
    "AURAIYA",
    "AYODHYA",
    "AZAMGARH",
    "BAGHPAT",
    "BAHRAICH",
    "BALLIA",
    "BALRAMPUR",
    "BANDA",
    "BARABANKI",
    "BAREILLY",
    "BASTI",
    "BHADOHI",
    "BIJNOR",
    "BUDAUN",
    "BULANDSHAHR",
    "CHANDAULI",
    "CHITRAKOOT",
    "DEORIA",
    "ETAH",
    "ETAWAH",
    "FARRUKHABAD",
    "FATEHPUR",
    "FIROZABAD",
    "GAUTAM BUDDHA NAGAR",
    "GHAZIABAD",
    "GHAZIPUR",
    "GONDA",
    "GORAKHPUR",
    "HAMIRPUR",
    "HAPUR",
    "HARDOI",
    "HATHRAS",
    "JALAUN",
    "JAUNPUR",
    "JHANSI",
    "KANNAUJ",
    "KANPUR DEHAT",
    "KANPUR NAGAR",
    "Kasganj",
    "KAUSHAMBI",
    "KHERI",
    "KUSHI NAGAR",
    "LALITPUR",
    "LUCKNOW",
    "MAHARAJGANJ",
    "MAHOBA",
    "MAINPURI",
    "MATHURA",
    "MAU",
    "MEERUT",
    "MIRZAPUR",
    "MORADABAD",
    "MUZAFFARNAGAR",
    "PILIBHIT",
    "PRATAPGARH",
    "PRAYAGRAJ",
    "RAE BARELI",
    "RAMPUR",
    "SAHARANPUR",
    "SAMBHAL",
    "SANT KABEER NAGAR",
    "SHAHJAHANPUR",
    "SHAMLI",
    "SHRAVASTI",
    "SIDDHARTH NAGAR",
    "SITAPUR",
    "SONBHADRA",
    "SULTANPUR",
    "UNNAO",
    "VARANASI"
]

last_processed_month = ""
last_processed_district = ""

driver = webdriver.Chrome()
driver.get(LOGIN_URL)
input("Opening portal, pls login and press enter to conitnue...")

print("Selecting data-entry options...")
driver.find_element(By.XPATH, "//span[contains(.,\'Data Entry\')]").click()
driver.implicitly_wait(0.2)
driver.find_element(By.CSS_SELECTOR, "#submenu84 .menu-text").click()

# Waiting for initial scheme options to appear
WebDriverWait(driver, 10).until(lambda d: d.find_element(By.ID, "schemeLabel"))

scheme_dropdown = driver.find_element(By.ID, "schemeName")
state_dropdown = driver.find_element(By.ID, "state")
year_dropdown = driver.find_element(By.ID, "year")
month_dropdown = driver.find_element(By.ID, "month")
district_dropdown = driver.find_element(By.ID, "district")

# Scheme
scheme_dropdown.click()
scheme_dropdown.find_element(By.XPATH, f"//option[. = '{SCHEME_NAME}']").click()

# State
state_dropdown.click()
state_dropdown.find_element(By.XPATH, f"//option[. = '{STATE}']").click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#state > option:nth-child(2)")))

# Year
year_dropdown.click()
year_dropdown.find_element(By.XPATH, f"//option[. = '{FINANCIAL_YEAR}']").click()

try:
    # Resume logic
    if RESUME:
        print("Resume flag set, resuming from last processed month and district...")
        print("Month - ", START_MONTH)
        print("District - ", START_DISTRICT)

        # Get the index of the starting month
        start_month_index = SCHEME_MONTHS.index(START_MONTH)
        
        # Get the index of the starting district
        start_district_index = DISTRICTS.index(START_DISTRICT)
    else:
        start_month_index = 0
        start_district_index = 0
    
    for month in SCHEME_MONTHS[start_month_index:]:
        last_processed_month = month

        print("Reading excel file...")
        try:
            df = pd.read_excel(EXCEL_FILE, sheet_name=month)
        except ValueError:
            print("Month not found in data, skipping...")
            continue

        # Month
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#month > option:nth-child(1)")))
        month_dropdown.click()
        month_dropdown.find_element(By.XPATH, f"//option[. = '{month}']").click()

        # Close "Please select district" popup
        with contextlib.suppress(NoSuchElementException, ElementNotInteractableException):
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "close")))
            driver.find_element(By.LINK_TEXT, "×").click()
            driver.implicitly_wait(1)

        # Close "Previous Month Beneficiary Details" popup
        with contextlib.suppress(NoSuchElementException, ElementNotInteractableException):
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#myModal > div > div > div.modal-header.modal-header-info > h2")))
            driver.find_element(By.CSS_SELECTOR, "#closebutton").click()
            driver.implicitly_wait(1)
        
        for j, district in enumerate(DISTRICTS[start_district_index:], start=start_district_index):
            last_processed_district = district
            
            # District
            district_dropdown.click()
            district_dropdown.find_element(By.XPATH, f"//option[. = '{district}']").click()

            # Close "Previous Month Beneficiary Details" popup
            with contextlib.suppress(NoSuchElementException, ElementNotInteractableException):
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#myModal > div > div > div.modal-header.modal-header-info > h2")))
                driver.find_element(By.CSS_SELECTOR, "#closebutton").click()
                driver.implicitly_wait(5)
            
            clear_terminal()
            print(f"------------------ {SCHEME_NAME} ------------------")
            print()
            print(f"------------------ {month} ------------------")
            print()
            print(f"------ {district} ------")
            
            # Get district name from the dataframe
            district_in_data = df.loc[j + 1, "Scheme Name"]
            
            # Get the corresponding row from the DataFrame
            row = df[df["Scheme Name"] == district_in_data].squeeze()

            # Fill in the form fields based on the data
            #
            # Handling some edge cases where the previous data is different from the one in the portal
            update_beneficiary_field(driver, "numberofBenificiaries", row, "#noOfBen > msgcomp", "No. of beneficiaries through Normative Central & State share(Should be unique cumulative)")
            close_annoying_popup(driver)
            
            update_beneficiary_field(driver, "numberofAdditionalBenificiaries", row, "#noOfaddBeneficiary > msgcomp", "No. of additional beneficiaries supported by State , if any (Should be unique cumulative)")
            close_annoying_popup(driver)
            
            update_beneficiary_field(driver, "numberofBenificiariesRecordDigitized", row, "#noOfBeneficiaryRecordDizited > msgcomp", "No. of beneficiaries record digitized(Should be unique cumulative)")
            close_annoying_popup(driver)
            
            update_beneficiary_field(driver, "numberofAadharAuthenticated", row, "#noOfAadhar > msgcomp", "No. of Aadhaar authenticated and seeded Beneficiaries (Should be unique cumulative)")
            close_annoying_popup(driver)
            
            update_beneficiary_field(driver, "totalMobileNumberCaptured", row, "#totalMobileCapturerd > msgcomp", "No. of beneficiaries for whom mobile number is captured")
            close_annoying_popup(driver)
            
            central_funds = str(int(row["Central Share fund transferred"]))
            driver.find_element(By.ID, "centralSharedfundTransfered").clear()
            driver.find_element(By.ID, "centralSharedfundTransfered").send_keys(central_funds)

            normative_funds = str(int(row["Normative - State Share fund transferred"]))
            driver.find_element(By.ID, "stateSharedfundTransfered").clear()
            driver.find_element(By.ID, "stateSharedfundTransfered").send_keys(normative_funds)

            additional_funds = str(int(row["Additional State Contributed fund transferred"]))
            driver.find_element(By.ID, "additionalStateSharedfundTransfered").clear()
            driver.find_element(By.ID, "additionalStateSharedfundTransfered").send_keys(additional_funds)

            state_funds = str(int(row["State Share fund transferred to additional beneficiaries supported by State"]))
            driver.find_element(By.ID, "supportByState").clear()
            driver.find_element(By.ID, "supportByState").send_keys(state_funds)

            # Both the eletronic mode types value and total funds transferred value should be the same
            total_funds = str(sum(map(int, [central_funds, normative_funds, additional_funds, state_funds])))
            driver.find_element(By.ID, "electronicModesTypes").clear()
            driver.find_element(By.ID, "electronicModesTypes").send_keys(total_funds)

            driver.find_element(By.ID, "totalElectronicTransactionModes").clear()
            driver.find_element(By.ID, "totalElectronicTransactionModes").send_keys(str(row["Total No. of transactions For Electronics Modes"]))

            driver.find_element(By.ID, "totalNumberOfTransactionOtherModes").clear()
            driver.find_element(By.ID, "totalNumberOfTransactionOtherModes").send_keys("0")

            driver.find_element(By.ID, "otherModes").clear()
            driver.find_element(By.ID, "otherModes").send_keys("0")

            # Closing annoying "electronic modes should be equal to total funds" popup
            close_annoying_popup(driver)

            driver.find_element(By.ID, "depulicateRecords").clear()
            driver.find_element(By.ID, "depulicateRecords").send_keys("0")

            driver.find_element(By.ID, "numberOfGhost").clear()
            driver.find_element(By.ID, "numberOfGhost").send_keys("0")

            driver.find_element(By.ID, "otherSaving").clear()
            driver.find_element(By.ID, "otherSaving").send_keys("0")

            driver.find_element(By.ID, "savingAmounts").clear()
            driver.find_element(By.ID, "savingAmounts").send_keys("0")

            if DRY_RUN:
                input("Dry run completed, press enter to exit...")
                exit(0)

            if not SKIP_SUBMIT:
                # Submitting
                driver.find_element(By.ID, "lockbutton").click()

                # Wait for popup
                status = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#messgdec > div")))

                if "error" in status.text:
                    print("An error occured - ", status.text)
                    print("Current Month - ", month),
                    print("Current District - ", district)
                    print("Exiting...")
                    exit(1)
                
                # Closing popup
                element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.LINK_TEXT, "×")))
                element.click()
                driver.implicitly_wait(1)

            # Scroll to the top of the page
            driver.execute_script("window.scrollTo(0, 0);")
        
        if ONE_MONTH:
            input("One month completed, press enter to exit...")
            exit(0)
except Exception as e:
    print("An error occured - ", e)
    print("Last Processed Month - ", last_processed_month),
    print("Last Processed District - ", last_processed_district)
    with contextlib.suppress(NoSuchElementException, ElementNotInteractableException):
        error_element = driver.find_element(By.CSS_SELECTOR, "body > div:nth-child(3) > div > h3")

        if "expired" in error_element.text:
            print("Session expired, login again!")
            print("Exiting...")
            exit(0)
    raise e