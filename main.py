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
    def __init__(self, driver, XpathDict, FligthPath = None):
        self.XpathDict = XpathDict
        self.driver = driver
        self.FligthPath =  FligthPath

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
  
        day =  day = calendar.day_name[self.FligthPath["startDate"].weekday()] 

     
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
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################


listOne = []
XPathsDict = {
    "Button1": '//*[@id="cookie-popup-with-overlay"]/div/div[3]/button[2]', # first button to verify cookies
    "DepartureInput": '//*[@id="input-button__departure"]',
    "DestinationInput": '//*[@id="input-button__destination"]',
    "London Stansted": '//*[@id="ry-tooltip-3"]/div[2]/hp-app-controls-tooltips/fsw-controls-tooltips-container/fsw-controls-tooltips/fsw-destination-container/fsw-airports/div/fsw-airports-list/div[2]/div[1]/fsw-airport-item[8]',
    #"Knock": '//*[@id="ry-tooltip-1"]/div[2]/hp-app-controls-tooltips/fsw-controls-tooltips-container/fsw-controls-tooltips/fsw-origin-container/fsw-airports/div/fsw-airports-list/div[2]/div[1]/fsw-airport-item[4]'
    "Knock": '/html/body/ry-tooltip/div[2]/hp-app-controls-tooltips/fsw-controls-tooltips-container/fsw-controls-tooltips/fsw-origin-container/fsw-airports/div/fsw-airports-list/div[2]/div[1]/fsw-airport-item[4]/span/span',
    "SorryNoFlightsAvailable": "/html/body/flights-root/div/div/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/flight-list/p",
    "FlightDepartTime": '/html/body/flights-root/div/div/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/flight-list/div/flight-card/div/div/div[1]/div/flight-info/div[1]/span[1]',
    "FlightList": '/html/body/flights-root/div/div/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/flight-list'
}

airportDict = {"LdnStn": "STN",
    "Ancona":"AOI",
    "Knock": "NOC",
    "Dublin": "DUB"
    }

driver = webdriver.Chrome()


# Create the dictionary flight path here
FlightPath = {
    "Connection1": {"departure":airportDict['Dublin'],
                    "arrival": airportDict['LdnStn']},

    "Connection2": {"departure":airportDict['LdnStn'],
                    "arrival": airportDict['Ancona']},
        
    "startDate": datetime.date(2022, 2, 11),
    "endDate": datetime.date(2022, 2, 16)
}


action = Actions(driver, XPathsDict, FligthPath = FlightPath )


# Dates Here
#startDate = datetime.date.today()
datetartCopy = FlightPath["startDate"].strftime("%Y-%m-%d")
timeNow = datetime.datetime.now().strftime("%Y-%m-%d%H%m%S")


delta = datetime.timedelta(days=1)


dfList = []
for flightInfo in FlightPath:
    listOne = []
    if "Connection" in flightInfo:
        FlightPath["startDate"]  =  datetime.datetime.strptime(datetartCopy, "%Y-%m-%d") # reseting the dates back for the second run if needed

        departure = FlightPath[flightInfo]['departure']
        arrival = FlightPath[flightInfo]['arrival']
            

        while FlightPath["startDate"].date() <= FlightPath["endDate"]:
            dateStr = FlightPath["startDate"].strftime("%Y-%m-%d")

            url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originIata={departure}&destinationIata={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata={departure}&tpDestinationIata={arrival}"
            driver.get(url)
            time.sleep(5)

            action.ClickButton("Button1")
            currencySymbol = ""
            if not action.CheckFlightToday():
                lists = action.AcquireListOfFlights(dateStr = dateStr, departure = departure, arrival = arrival)
                listOne.extend(lists["listOne"])
            FlightPath["startDate"] += delta # increment day by 1
            enddateCopy = FlightPath["endDate"].strftime("%Y-%m-%d")


        c = ["departure","Arrival","Date","day","DepartTime","ArrivalTime",f"cost({lists['Currency']})" ]

        if flightInfo == "Connection1":
            df = pd.DataFrame(listOne, columns = c)
            df[f"cost({lists['Currency']})"] = df[f"cost({lists['Currency']})"].astype(float)
        if flightInfo == "Connection2":
            df2 = pd.DataFrame(listOne, columns = c)
            df2[f"cost({lists['Currency']})"] = df2[f"cost({lists['Currency']})"].astype(float)
            #df.to_excel(rf"C:\Users\35386\Documents\projects\seleniumRyanair\{departure}_{arrival}_{datetartCopy}_{enddateCopy}_{timeNow}.xlsx", index = False)
newDf = df.merge(df2, left_on='Date', right_on='Date')
newDF 
newDf.to_excel(rf"C:\Users\35386\Documents\projects\seleniumRyanair\{departure}_{arrival}_{datetartCopy}_{enddateCopy}_{timeNow}.xlsx", index = False)

driver.close()


