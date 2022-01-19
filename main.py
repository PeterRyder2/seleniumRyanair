import os
from selenium import webdriver
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
class Actions:
    def __init__(self, driver, XpathDict):
        self.XpathDict = XpathDict
        self.driver = driver

    def ClickButton(self, xpathKey = None):
        try:
            #time.sleep(10)
            self.driver.find_element_by_xpath(self.XpathDict[xpathKey]).click()
            #time.sleep(10)
            return True
            
        except Exception as err:
            return False

    def InputData(self, xpathKey =None , input = None):
        try:
            e = self.driver.find_element_by_xpath(self.XpathDict[xpathKey])
            
            e.click()
            e.send_keys(Keys.CONTROL, 'a')
            e.send_keys(Keys.DELETE)
            e.send_keys(input)
            e.send_keys(Keys.ENTER)

            k = self.driver.find_element_by_xpath(self.XpathDict[input])
            k.click()


            
                        
            return True
        except Exception as err:
            print(err)
            return False
 
XPathsDict = {
    "Button1": '//*[@id="cookie-popup-with-overlay"]/div/div[3]/button[2]', # first button to verify cookies
    "DepartureInput": '//*[@id="input-button__departure"]',
    "DestinationInput": '//*[@id="input-button__destination"]',
    "London Stansted": '//*[@id="ry-tooltip-3"]/div[2]/hp-app-controls-tooltips/fsw-controls-tooltips-container/fsw-controls-tooltips/fsw-destination-container/fsw-airports/div/fsw-airports-list/div[2]/div[1]/fsw-airport-item[8]',
    #"Knock": '//*[@id="ry-tooltip-1"]/div[2]/hp-app-controls-tooltips/fsw-controls-tooltips-container/fsw-controls-tooltips/fsw-origin-container/fsw-airports/div/fsw-airports-list/div[2]/div[1]/fsw-airport-item[4]'
    "Knock": '/html/body/ry-tooltip/div[2]/hp-app-controls-tooltips/fsw-controls-tooltips-container/fsw-controls-tooltips/fsw-origin-container/fsw-airports/div/fsw-airports-list/div[2]/div[1]/fsw-airport-item[4]/span/span'
}
driver = webdriver.Chrome()
driver.get('https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut=2022-01-22&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originIata=NOC&destinationIata=STN&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate=2022-01-22&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata=NOC&tpDestinationIata=STN')

"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut=2022-01-22&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originIata=NOC&destinationIata=STN&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate=2022-01-22&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata=NOC&tpDestinationIata=STN"
"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut=2022-02-03&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originIata=STN&destinationIata=AOI&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate=2022-02-03&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata=STN&tpDestinationIata=AOI"
#driver.get('https://www.ryanair.com/ie/en')
action = Actions(driver, XPathsDict)


#time.sleep(10)

action.ClickButton( "Button1")


action.InputData("DepartureInput", "Knock")