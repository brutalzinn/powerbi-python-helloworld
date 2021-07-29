import re
import pandas as pd
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv


load_dotenv()

link = 'https://www.worldometers.info/'
REST_API_URL = os.environ.get("POWER_BI") #'https://api.powerbi.com/beta/aa495f2c-d37e-4b58-ab95-bf0874a3adb2/datasets/dc4a8d58-508b-4725-be3f-1366644dcda1/rows?redirectedFromSignup=1&key=jjNsu5i%2FozyjKYpoMNI3Qd3Da%2FEk7jXMLOlL0LLzSGIinLjriRqmcrt0qp3Lp%2Bfa78%2BnRFStu%2FA0Y9jnRbLkWQ%3D%3D'
def parseNumber(text):
    try:
        # First we return None if we don't have something in the text:
        if text is None:
            return None
        if isinstance(text, int) or isinstance(text, float):
            return text
        text = text.strip()
        if text == "":
            return None
        # Next we get the first "[0-9,. ]+":
        n = re.search("-?[0-9]*([,. ]?[0-9]+)+", text).group(0)
        n = n.strip()
        if not re.match(".*[0-9]+.*", text):
            return None
        # Then we cut to keep only 2 symbols:
        while " " in n and "," in n and "." in n:
            index = max(n.rfind(','), n.rfind(' '), n.rfind('.'))
            n = n[0:index]
        n = n.strip()
        # We count the number of symbols:
        symbolsCount = 0
        for current in [" ", ",", "."]:
            if current in n:
                symbolsCount += 1
        # If we don't have any symbol, we do nothing:
        if symbolsCount == 0:
            pass
        # With one symbol:
        elif symbolsCount == 1:
            # If this is a space, we just remove all:
            if " " in n:
                n = n.replace(" ", "")
            # Else we set it as a "." if one occurence, or remove it:
            else:
                theSymbol = "," if "," in n else "."
                if n.count(theSymbol) > 1:
                    n = n.replace(theSymbol, "")
                else:
                    n = n.replace(theSymbol, ".")
        else:
            # Now replace symbols so the right symbol is "." and all left are "":
            rightSymbolIndex = max(n.rfind(','), n.rfind(' '), n.rfind('.'))
            rightSymbol = n[rightSymbolIndex:rightSymbolIndex+1]
            if rightSymbol == " ":
                return parseNumber(n.replace(" ", "_"))
            n = n.replace(rightSymbol, "R")
            leftSymbolIndex = max(n.rfind(','), n.rfind(' '), n.rfind('.'))
            leftSymbol = n[leftSymbolIndex:leftSymbolIndex+1]
            n = n.replace(leftSymbol, "L")
            n = n.replace("L", "")
            n = n.replace("R", ".")
        # And we cast the text to float or int:
        n = float(n)
        if n.is_integer():
            return int(n)
        else:
            return n
    except: pass
    return None
def get_population_count(wait):
    item = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="c26"]/div[1]')))
    florest = wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="c24"]/div[1]')))
    world_pop = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="c1"]/div[1]')))
    florest_data = florest.find_element(By.CLASS_NAME, 'rts-counter')
    world_pop_data = world_pop.find_element(By.CLASS_NAME, 'rts-counter')
    # print('florest',florest_data.text)
    # print('world pópulation',world_pop_data.text)
    return [parseNumber(florest_data.text),parseNumber(world_pop_data.text)]

   ## return item

with webdriver.Chrome() as driver:
    wait = WebDriverWait(driver,10)
    driver.get(link)
    while True:
        data_raw = []
        for i in range(1):
            row = get_population_count(wait)
            data_raw.append(row)
            print("Raw data - ", data_raw)

        # set the header record
        HEADER = ["floresta", "populacao"]

        data_df = pd.DataFrame(data_raw, columns=HEADER)
        data_json = bytes(data_df.to_json(orient='records'), encoding='utf-8')
        print("JSON dataset", data_json)

        # Post the data on the Power BI API
        req = requests.post(REST_API_URL, data_json)

        print("Data posted in Power BI API")
        time.sleep(2)
       
        
       