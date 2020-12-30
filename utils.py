from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

TIMEOUT = 10

def convert_str_to_number(x):
    total_stars = 0
    num_map = {'K':1000, 'M':1000000, 'B':1000000000}
    if x.isdigit():
        total_stars = int(x)
    else:
        if len(x) > 1:
            x = x.replace(" ", "")
            x = x.replace(",", ".")
            total_stars = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(total_stars)


def notNone(string):
    if string is None:
        return ""
    return string


def doesExistXP(chrome, selector):
    try:
        elem = chrome.find_element_by_xpath(selector)
        return elem is None
    except:
        return False


def doesExist(chrome, selector):
    try:
        elem = chrome.find_element_by_css_selector(selector)
        return elem is not None
    except:
        return False


def clickIfExistXP(chrome, selector):
    try :
        element = chrome.find_element_by_xpath(selector)
        element.click()
    finally:
        return


def clickIfExist(chrome, selector):
    try :
        element = chrome.find_element_by_css_selector(selector)
        element.click()
    finally:
        return


def getWhenExist(chrome, elem):
    try:
        WebDriverWait(chrome, TIMEOUT).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR, elem)))
        return notNone(chrome.find_element_by_css_selector(elem).text)
    except:
        return ""


def getWhenExistXP(chrome, elem):
    try:
        WebDriverWait(chrome, TIMEOUT).until(expected_conditions.presence_of_element_located((By.XPATH, elem)))
        return notNone(chrome.find_element_by_xpath(elem).text)
    except:
        return ""



def clickWhenExistXP(chrome, elem):
    try:
        element = WebDriverWait(chrome, TIMEOUT).until(expected_conditions.element_to_be_clickable((By.XPATH, elem)))
        element.click()
    finally:
        return



def clickWhenExist(chrome, elem):
    try:
        element = WebDriverWait(chrome, TIMEOUT).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, elem)))
        element.click()
    finally:
        return


def sendText(chrome, selector, text):
    try:
        element = WebDriverWait(chrome, TIMEOUT).until(expected_conditions.element_to_be_clickable((By.XPATH, selector)))
        element.send_keys(text)
    finally:
        return