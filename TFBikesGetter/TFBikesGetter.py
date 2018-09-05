import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pathlib import Path
import shutil
import os
import filecmp

from TFTask.TFTask import TFTask


class TFWeatherGetter(TFTask):
    __logger = logging.getLogger(__name__)
    __DL_FILE_NAME = "export_LICZNIKI.csv"


    def __init__(self, outfile, name, interval_min=0, interval_h=0):

        TFTask.__init__(self, name, interval_min, interval_h)
        self.__outfile = outfile

    def task(self):

        self.__getNewCsv()

        out_file = Path(self.__outfile)

        if out_file.is_file():

            if not filecmp(__DL_FILE_NAME, self.__outfile):
                os.remove(self.__outfile)
                shutil.move(self.__DL_FILE_NAME, self.__outfile)

            else:
                os.remove(self.__DL_FILE_NAME)

        else:
            shutil.move(self.__DL_FILE_NAME, self.__outfile)


    def __getNewCsv(self):

        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory": "./"}
        chromeOptions.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome(chrome_options=chromeOptions)

        browser.get("https://view-awesome-table.com/-K_QsMprVPERjxnx2bml/view")

        delay = 10

        try:

            myElem = WebDriverWait(browser, delay).until( EC.presence_of_element_located((By.CLASS_NAME, 'at-action-menu-trigger')))
            browser.find_element_by_class_name('at-action-menu-trigger').click()
            self.__logger.info("Page is ready!")
            myElem = WebDriverWait(browser, delay).until(EC.presence_of_element_located((By.ID, 'at-button-export')))
            browser.find_element_by_id('at-button-export').click()

        except TimeoutException:
            self.__logger.error("Loading took too much time!")

        browser.quit()


