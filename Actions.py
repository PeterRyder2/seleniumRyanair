from locale import currency
import os
from selenium import webdriver
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.common.keys import Keys
import datetime
import calendar 


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


    def CheckFlightToday(self):
        try:
            text =   driver.find_element_by_xpath(self.XpathDict["SorryNoFlightsAvailable"]).text
            noFlighttext = 'Sorry, there are no flights available on this day'

            return True if  text == noFlighttext else False
        except Exception as err:

            return False


    def  AcquireListOfFlights(self,dateStr = None, departure = None, arrival = None):
        listOne = []
        Departtime, ArrivalTime, price  = (None,)*3

        str1 =   driver.find_element_by_xpath(self.XpathDict["FlightList"]).text

        str1 = str1.split("Ryanair")
        if "" in str1:
                str1.remove("")
  
        day =  day = calendar.day_name[startDate.weekday()] 

     
        stringsToremove = "€£"
        for values in str1:
            
            splits = values.split("\n")
            if "" in splits:
                splits.remove("")
            splits = [value for value in splits if value != ""]
            
            for count, i in enumerate(splits):
                if ":" in splits[count] and Departtime == None :
                
                    Departtime = i

                elif  "€" in  splits[count] or "£" in i and price  == None:
                    if "€" in  splits[count]: Currency = "€"
                    else: Currency = "£"
                    price = i
                elif  ":" in  splits[count] and ArrivalTime == None:
                    ArrivalTime = i
            
            for i in stringsToremove:
                price = price.replace(i, "")


            listOne.append([departure,arrival,dateStr,day, Departtime,ArrivalTime,price])
            Departtime,ArrivalTime,price = (None,)*3 # reassign values to None
            #arrivalTime =splits[1]

        return {"listOne":listOne, "Currency": Currency}

