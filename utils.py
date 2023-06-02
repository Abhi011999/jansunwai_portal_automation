import os
import subprocess
import contextlib

from thefuzz import fuzz
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *

def compare(string1, string2):
    similarity = fuzz.ratio(string1, string2)
    return similarity > 90

    # similarity_ratio = fuzz.token_sort_ratio(string1, string2)
    # partial_ratio = fuzz.partial_ratio(string1, string2)
    # token_set_ratio = fuzz.token_set_ratio(string1, string2)

    # average_similarity = (similarity_ratio + partial_ratio + token_set_ratio) / 3
    # return average_similarity > 70

def clear_terminal():
    subprocess.call('clear' if os.name == 'posix' else 'cls', shell=True)


def update_beneficiary_field(driver, element_id, row, prev_element_selector, row_key):
    prev_elements = driver.find_elements(By.CSS_SELECTOR, prev_element_selector)
    val = int(row[row_key])

    if len(prev_elements) > 0:
        prev_val = int(prev_elements[-1].text.split("=")[1])
        val = max(prev_val, val)

    element = driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(str(val))


def close_annoying_popup(driver):
    with contextlib.suppress(NoSuchElementException, ElementNotInteractableException):
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, "close")))
        WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.LINK_TEXT, "×"))).click()
        driver.implicitly_wait(1)