#%%
from locale import currency
from selenium import webdriver
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import calendar 
import numpy as np
from time import strptime
import datetime 
import urllib.request
from datetime import date, timedelta
from currency_converter import ECB_URL, CurrencyConverter
import os.path as op
import os
import sys

class Actions:
    def __init__(self, driver, XpathDict, FligthPath = None):
        self.XpathDict = XpathDict
        self.driver = driver
        self.FligthPath =  FligthPath


  
    def DownloadForexFile(self):
        '''
        Dowloads the FOREX rates adn returns the csv it contains
        if already it just returns the filename
        '''
        ForexFolder = r"C:\Users\35386\Documents\projects\seleniumRyanair\ForexLoads"
        ForexFolderContents  = [name for name in os.listdir(ForexFolder)]
        todaysFileName = f"ecb_{date.today():%Y%m%d}.zip"
        if len(ForexFolderContents) > 0:
            for i in ForexFolderContents:
                if i != todaysFileName:
                    os.remove(os.path.join(ForexFolder, i ))
        
        filename = os.path.join(ForexFolder,  f"ecb_{date.today():%Y%m%d}.zip")
        
        if not op.isfile(filename):
            urllib.request.urlretrieve(ECB_URL, filename)
        return filename


    def ClickButton(self, xpathKey = None):
        try:
            #time.sleep(10)
            self.driver.find_element(By.XPATH,self.XpathDict[xpathKey]).click()
            #time.sleep(10)
            return True
            
        except Exception as err:
            return False

    def InputData(self, xpathKey =None , input = None):
        try:
            e = self.driver.find_element(By.XPATH,self.XpathDict[xpathKey])
            
            e.click()
            e.send_keys(Keys.CONTROL, 'a')
            e.send_keys(Keys.DELETE)
            e.send_keys(input)
            e.send_keys(Keys.ENTER)

            k = self.driver.find_element(By.XPATH,self.XpathDict[input])
            k.click()


            
                        
            return True
        except Exception as err:
            print(err)
            return False


    def CheckFlightToday(self):
        try:
            text =   driver.find_element(By.XPATH, self.XpathDict["SorryNoFlightsAvailable"]).text
            noFlighttext = 'Sorry, there are no flights available on this day'

            return True if  text == noFlighttext else False
        except Exception as err:

            return False


    def  AcquireListOfFlights(self,dateStr = None, departure = None, arrival = None, url = None):
        listOne = []
        Departtime, ArrivalTime, price  = (None,)*3

        str1 =   driver.find_element(By.XPATH,self.XpathDict["FlightList"]).text

        str1 = str1.split("Ryanair")
        if "" in str1:
                str1.remove("")
  
        day =  day = calendar.day_name[self.FligthPath["startDate"].weekday()] 
        month = self.FligthPath["startDate"].strftime("%b")
     
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


            listOne.append([departure,arrival,dateStr,day,month,  Departtime,ArrivalTime,price, url])
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
    "Dublin": "DUB",
    "Rimini": "RMI"
    }
options = Options()
options.add_argument('--headless')


driver = webdriver.Chrome(chrome_options=options)


# Create the dictionary flight path here
FlightPath = {
    "From": "Ancona",
    "To": "Knock",
    "Connection1": {"departure":airportDict['Knock'],
                    "arrival": airportDict['LdnStn']},

    "Connection2": {"departure":airportDict['LdnStn'],
                    "arrival": airportDict['Ancona']},
        
    "startDate": datetime.date(2022, 6, 11),
    "endDate": datetime.date(2022, 6, 22)
}


action = Actions(driver, XPathsDict, FligthPath = FlightPath )
currConvert = CurrencyConverter(action.DownloadForexFile(), fallback_on_missing_rate=True)

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
                lists = action.AcquireListOfFlights(dateStr = dateStr, departure = departure, arrival = arrival, url = url)
                listOne.extend(lists["listOne"])
            FlightPath["startDate"] += delta # increment day by 1
            enddateCopy = FlightPath["endDate"].strftime("%Y-%m-%d")


        c = ["departure","Arrival","Date","day", "month", "DepartTime","ArrivalTime",f"cost({lists['Currency']})", "url" ]
      
        if flightInfo == "Connection1":
            df = pd.DataFrame(listOne, columns = c)
            df[f"cost({lists['Currency']})"] = df[f"cost({lists['Currency']})"].astype(float)
        if flightInfo == "Connection2":
            df2 = pd.DataFrame(listOne, columns = c)
            df2[f"cost({lists['Currency']})"] = df2[f"cost({lists['Currency']})"].astype(float)
            #df.to_excel(rf"C:\Users\35386\Documents\projects\seleniumRyanair\{departure}_{arrival}_{datetartCopy}_{enddateCopy}_{timeNow}.xlsx", index = False)


newDF = df.merge(df2, left_on='Date', right_on='Date')
if newDF.shape[0] == 0:
    print("Nothing to Merge")
    sys.exit()

########### Post processing ####################

columns = [i for i in newDF.columns if "£"  in i]
newDF["Total(€)"]  = newDF["cost(€)"]

for pound in columns:
    newDF[f"{pound}_Convert"] =  newDF[pound].apply(lambda x: currConvert.convert(x, 'GBP', 'EUR', date=date.today() - timedelta(days = 1)))
    newDF["Total(€)"] = newDF["Total(€)"] + newDF[f"{pound}_Convert"]



newDF["datetimeDepartX"]= [datetime.datetime.strptime(i, "%H:%M") for i in newDF["DepartTime_x"] ]
newDF["datetimeArriveX"] = [datetime.datetime.strptime(i, "%H:%M") for i in newDF["ArrivalTime_x"] ]

newDF["datetimeDepartY"]= [datetime.datetime.strptime(i, "%H:%M") for i in newDF["DepartTime_y"] ]
newDF["datetimeArriveY"] = [datetime.datetime.strptime(i, "%H:%M") for i in newDF["ArrivalTime_y"] ]

newDF['suits'] = np.where(newDF["datetimeArriveX"]  <=  newDF["datetimeDepartY"] , True, False)
newDF['layovertime'] =  np.where(newDF["suits"] == True, newDF["datetimeDepartY"] - newDF["datetimeArriveX"], False  ) 
newDF['layovertime'] =  newDF['layovertime'].astype(str)
newDF["TotalTravelTime"] =  np.where(newDF["suits"] == True, newDF["datetimeArriveY"] - newDF["datetimeDepartX"] , False  ) 
newDF['TotalTravelTime'] =  newDF['TotalTravelTime'].astype(str)
newDF["Total(€)"] = newDF["Total(€)"].apply(lambda x: round(x,2))

################################# END POSTPROCESSING ##############################

newDF.to_excel(rf"C:\Users\35386\Documents\projects\seleniumRyanair\{FlightPath['From']}_TO_{FlightPath['To']}_{datetartCopy}_{enddateCopy}_{timeNow}.xlsx")

driver.close()



# %%
