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
import zipfile


class Actions:
    def __init__(self, driver, XpathDict, FligthPath = None, airportList = None):
        self.XpathDict = XpathDict
        self.driver = driver
        self.FlightPath =  FligthPath
        self.delta = datetime.timedelta(days=1)
        self.airportList = airportList

    def DirectFlightDF(self,departure, arrival, newDF ):
        listOne = []
        departure = self.airportList[departure]
        arrival = self.airportList[arrival]
        while self.FlightPath["startDate"].date() <= self.FlightPath["endDate"]:
                dateStr = self.FlightPath["startDate"].strftime("%Y-%m-%d")

                url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originIata={departure}&destinationIata={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata={departure}&tpDestinationIata={arrival}"
                self.driver.get(url)
                time.sleep(5)

                self.ClickButton("Button1")
                currencySymbol = ""
                if not self.CheckFlightToday():
                    lists = self.AcquireListOfFlights(driver = self.driver,dateStr = dateStr, departure = departure, arrival = arrival, url = url)
                    listOne.extend(lists["listOne"])
                self.FlightPath["startDate"] += self.delta # increment day by 1
                enddateCopy = self.FlightPath["endDate"].strftime("%Y-%m-%d")

        if len(listOne) > 0: 
            #c = ["departure","Arrival","Date","day", "month", "DepartTime","ArrivalTime",f"cost({lists['Currency']})", "url" ]
            c = ["departure_x",	"Arrival_x", "Date", "day_x","month_x",	"DepartTime_x",	"ArrivalTime_x", f"cost({lists['Currency']})", "url_x"]

            df = pd.DataFrame(listOne, columns = c)
            #newDF = newDF.merge(df, left_on='Date', right_on='Date')
            newDF = newDF.append(df, ignore_index=True)
            return newDF
        else:
            return None
  
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
        

        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(ForexFolder)
            f = [i for i in os.listdir(ForexFolder) if i.endswith(".csv")]
            csvname = os.path.join(ForexFolder, f[0])
            df = pd.read_csv(csvname)
            date1 =  df.iloc[0:1]["Date"].values[0]
            os.remove(csvname)

        return {"filename": filename, "date_to_use": datetime.datetime.strptime(date1, "%Y-%M-%d")}


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
            text =   self.driver.find_element(By.XPATH, self.XpathDict["SorryNoFlightsAvailable"]).text
            noFlighttext = 'Sorry, there are no flights available on this day'

            return True if  text == noFlighttext else False
        except Exception as err:

            return False

    def Checkdeparture(self, i):
        if i in self.airportList.keys() or i in self.airportList.values():
            return i
        else: return None


    def  AcquireListOfFlights(self,driver = None ,dateStr = None, departure = None, arrival = None, url = None):
        listOne = []
        DepartString, ArriveString, Departtime, ArrivalTime, price  = (None,)*5

        time.sleep(5)
        str1 =   driver.find_element(By.XPATH,self.XpathDict["FlightList"]).text

        str1 = str1.split("Ryanair")
        if "" in str1:
                str1.remove("")
  
        day =  day = calendar.day_name[self.FlightPath["startDate"].weekday()] 
        month = self.FlightPath["startDate"].strftime("%b")
     
        stringsToremove = "€£"
        for values in str1:
            
            splits = values.split("\n")
            if "" in splits:
                splits.remove("")
            splits = [value for value in splits if value != ""]
            
            for count, i in enumerate(splits):
                
                if self.Checkdeparture(i)  and DepartString == None:
                    DepartString = i 
                elif self.Checkdeparture(i) and ArriveString == None:
                    ArriveString = i
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


            listOne.append([DepartString,ArriveString,dateStr,day,month,  Departtime,ArrivalTime,price, url])
            DepartString, ArriveString,Departtime,ArrivalTime,price = (None,)*5 # reassign values to None
            #arrivalTime =splits[1]

        return {"listOne":listOne, "Currency": Currency}
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################

# def main():

#     listOne = []
#     XPathsDict = {
#         "Button1": '//*[@id="cookie-popup-with-overlay"]/div/div[3]/button[2]', # first button to verify cookies
#         "FlightList": '/html/body/flights-root/div/div/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/flight-list'
#     }

#     airportDict = {"London Stansted": "STN",
#         "London Luton": "LTN",
#         "Ancona":"AOI",
#         "Bologna": "BLQ",
#         "Knock": "NOC",
#         "Dublin": "DUB",
#         "Rimini": "RMI",
#         "Milan Bergamo": "BGY",
#         "LondonAll": "LON",
#         "Pescara": "PSR",
#         "Perugia": "PEG",
#         "MilanAll": "MIL",
#         "CHECKURL": ["LON", "MIL"] # add here if you user the all selection eg.  London ALL
#         }
#     options = Options()
#     #options.add_argument('--headless')


#     driver = webdriver.Chrome(chrome_options=options)

#     FlightPath = {

#         "Connection1": {"departure":airportDict['MilanAll'],
#                         "arrival": airportDict['LondonAll']},

#         "Connection2": {"departure":airportDict['LondonAll'],
#                         "arrival": airportDict['Knock']},
        
       
#         "startDate": datetime.date(2022, 3, 1 ),
#         "endDate": datetime.date(2022, 3, 4)
#     }
#     FlightPath["From"]= FlightPath['Connection1']['departure']
#     FlightPath["To"]= FlightPath['Connection2']['arrival']

#     action = Actions(driver, XPathsDict, FligthPath = FlightPath, airportList=airportDict )
#     ForexFileData = action.DownloadForexFile()
#     currConvert = CurrencyConverter(ForexFileData['filename'], fallback_on_missing_rate=True)
#     # Dates Here
#     #startDate = datetime.date.today()
#     datetartCopy = FlightPath["startDate"].strftime("%Y-%m-%d")
#     timeNow = datetime.datetime.now().strftime("%Y-%m-%d%H%m%S")

#     delta = datetime.timedelta(days=1)

#     dfList = []
#     for flightInfo in FlightPath:
#         listOne = []
#         if "Connection" in flightInfo:
#             FlightPath["startDate"]  =  datetime.datetime.strptime(datetartCopy, "%Y-%m-%d") # reseting the dates back for the second run if needed

#             departure = FlightPath[flightInfo]['departure']
#             arrival = FlightPath[flightInfo]['arrival']
                

#             while FlightPath["startDate"].date() <= FlightPath["endDate"]:
#                 dateStr = FlightPath["startDate"].strftime("%Y-%m-%d")
#                 if arrival in airportDict["CHECKURL"] or departure in airportDict["CHECKURL"]:
#                     if arrival in airportDict["CHECKURL"] and departure in airportDict["CHECKURL"]:
#                         url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originMac={departure}&destinationMac={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginMac={departure}&tpDestinationMac={arrival}"
#                     elif departure in airportDict["CHECKURL"]:
#                         url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&discount=0&isReturn=false&promoCode=&originMac={departure}&destinationIata={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginMac={departure}&tpDestinationIata={arrival}"
#                     elif arrival in airportDict["CHECKURL"]:
#                         url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&discount=0&isReturn=false&promoCode=&originMac={departure}&destinationIata={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginMac={departure}&tpDestinationIata={arrival}"
#                 else:
#                     # there is no ALL search terms in the arrival or destinations 
#                     url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originIata={departure}&destinationIata={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata={departure}&tpDestinationIata={arrival}"
                
#                 driver.get(url)
#                 time.sleep(5)

#                 action.ClickButton("Button1")
#                 currencySymbol = ""
#                 if not action.CheckFlightToday():
#                     lists = action.AcquireListOfFlights(driver = driver,dateStr = dateStr, departure = departure, arrival = arrival, url = url)
#                     listOne.extend(lists["listOne"])
#                 FlightPath["startDate"] += delta # increment day by 1
#                 enddateCopy = FlightPath["endDate"].strftime("%Y-%m-%d")


#             c = ["departure","Arrival","Date","day", "month", "DepartTime","ArrivalTime",f"cost({lists['Currency']})", "url" ]
        
#             if flightInfo == "Connection1":
#                 df = pd.DataFrame(listOne, columns = c)
#                 df[f"cost({lists['Currency']})"] = df[f"cost({lists['Currency']})"].astype(float)
#             if flightInfo == "Connection2":
#                 df2 = pd.DataFrame(listOne, columns = c)
#                 df2[f"cost({lists['Currency']})"] = df2[f"cost({lists['Currency']})"].astype(float)
#                 #df.to_excel(rf"C:\Users\35386\Documents\projects\seleniumRyanair\{departure}_{arrival}_{datetartCopy}_{enddateCopy}_{timeNow}.xlsx", index = False)

#     FlightPath["startDate"]  =  datetime.datetime.strptime(datetartCopy, "%Y-%m-%d") # reseting the dates back for the second run if needed

#     newDF = df.merge(df2, left_on='Date', right_on='Date')
#     if newDF.shape[0] == 0:
#         print("Nothing to Merge")
#         sys.exit()

#     ########### Post processing ####################

#     columns = [i for i in newDF.columns if "£"  in i]
#     newDF["Total(€)"]  = newDF["cost(€)"]

#     for pound in columns:
#         newDF[f"{pound}_Convert"] =  newDF[pound].apply(lambda x: currConvert.convert(x, 'GBP', 'EUR', ForexFileData['date_to_use']))
#         newDF["Total(€)"] = newDF["Total(€)"] + newDF[f"{pound}_Convert"]



#     newDF["datetimeDepartX"]= [datetime.datetime.strptime(i, "%H:%M") for i in newDF["DepartTime_x"] ]
#     newDF["datetimeArriveX"] = [datetime.datetime.strptime(i, "%H:%M") for i in newDF["ArrivalTime_x"] ]

#     newDF["datetimeDepartY"]= [datetime.datetime.strptime(i, "%H:%M") for i in newDF["DepartTime_y"] ]
#     newDF["datetimeArriveY"] = [datetime.datetime.strptime(i, "%H:%M") for i in newDF["ArrivalTime_y"] ]

#     newDF['suits'] = np.where(newDF["datetimeArriveX"]  <=  newDF["datetimeDepartY"] , True, False)
#     newDF['layovertime'] =  np.where(newDF["suits"] == True, newDF["datetimeDepartY"] - newDF["datetimeArriveX"], False  ) 
#     newDF['layovertime'] =  newDF['layovertime'].astype(str)
#     newDF["TotalTravelTime"] =  np.where(newDF["suits"] == True, newDF["datetimeArriveY"] - newDF["datetimeDepartX"] , False  ) 
#     newDF['TotalTravelTime'] =  newDF['TotalTravelTime'].astype(str)
#     newDF["Total(€)"] = newDF["Total(€)"].apply(lambda x: round(x,2))

#     newDF = newDF[newDF["suits"] == True]
    
#     # Full set of columns
#     # newDF = newDF["departure_x",
#     #             "Arrival_x",
#     #             "Date",
#     #             "day_x"	,
#     #             "month_x",
#     #             "DepartTime_x",
#     #             "ArrivalTime_x",
#     #             "cost(€)",
#     #             "url_x",
#     #             "departure_y",
#     #             "Arrival_y",
#     #             "day_y",
#     #             "month_y",
#     #             "DepartTime_y",
#     #             "ArrivalTime_y",
#     #             "cost(£)",
#     #             "url_y",
#     #             "Total(€)",
#     #             "cost(£)_Convert",
#     #             "datetimeDepartX",
#     #             "datetimeArriveX",
#     #             "datetimeDepartY",
#     #             "datetimeArriveY",
#     #             "suits",
#     #             "layovertime",
#     #             "TotalTravelTime"]


#     # Trimmed Columns
#     newDF = newDF[["departure_x",
#                 "Arrival_x",
#                 "Date",
#                 "day_x",
#                 "month_x",
#                 "DepartTime_x",
#                 "ArrivalTime_x",
#                 "departure_y",
#                 "Arrival_y",
#                 "DepartTime_y",
#                 "ArrivalTime_y",
#                 "Total(€)",
#                 "layovertime",
#                 "TotalTravelTime",
#                 "url_x",
#                 "url_y"]]

#     ################################# END POSTPROCESSING ##############################

#     #newDF = action.DirectFlightDF("Knock", "Milan Bergamo", newDF)
    

#     newDF.to_excel(rf"C:\Users\35386\Documents\projects\seleniumRyanair\{FlightPath['From']}_TO_{FlightPath['To']}_{datetartCopy}_{enddateCopy}_{timeNow}.xlsx", index  = False)

#     driver.close()


# main()



class FlightDataCreator():

    def __init__(self, startDate = None, endDate = None) -> None:
        self.airportDict = {"London Stansted": "STN",
        "London Luton": "LTN",
        "Ancona":"AOI",
        "Bologna": "BLQ",
        "Knock": "NOC",
        "Dublin": "DUB",
        "Rimini": "RMI",
        "Milan Bergamo": "BGY",
        "LondonAll": "LON",
        "Pescara": "PSR",
        "Perugia": "PEG",
        "MilanAll": "MIL",
        "CHECKURL": ["LON", "MIL"] # add here if you user the all selection eg.  London ALL
        }

        self.XPathsDict = {
        "Button1": '//*[@id="cookie-popup-with-overlay"]/div/div[3]/button[2]', # first button to verify cookies
        "FlightList": '/html/body/flights-root/div/div/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/flight-list'
        "So"
        }

        self.startDate = datetime.date(2022, 3, 1 ) 
        self.endDate = datetime.date(2022, 3, 4)
        self.options = Options()
        #self.options.add_argument('--headless')


        self.driver = webdriver.Chrome(chrome_options=self.options)
        self.FlightPath = {

            "Connection1": {"departure":self.airportDict['MilanAll'],
                            "arrival": self.airportDict['LondonAll']},

            "Connection2": {"departure":self.airportDict['LondonAll'],
                            "arrival": self.airportDict['Knock']},
            
        
            "startDate": self.startDate,
            "endDate": self.endDate
        }
        self.FlightPath["From"]= self.FlightPath['Connection1']['departure']
        self.FlightPath["To"]= self.FlightPath['Connection2']['arrival']


    def FLightFinder(self):
        action = Actions(self.driver, self.XPathsDict, FligthPath = self.FlightPath, airportList=self.airportDict )
        ForexFileData = action.DownloadForexFile()
        currConvert = CurrencyConverter(ForexFileData['filename'], fallback_on_missing_rate=True)
        # Dates Here
        #startDate = datetime.date.today()
        datetartCopy = self.FlightPath["startDate"].strftime("%Y-%m-%d")
        timeNow = datetime.datetime.now().strftime("%Y-%m-%d%H%m%S")

        delta = datetime.timedelta(days=1)

        dfList = []
        for flightInfo in self.FlightPath:
            listOne = []
            if "Connection" in flightInfo:
                self.FlightPath["startDate"]  =  datetime.datetime.strptime(datetartCopy, "%Y-%m-%d") # reseting the dates back for the second run if needed

                departure = self.FlightPath[flightInfo]['departure']
                arrival = self.FlightPath[flightInfo]['arrival']
                    

                while self.FlightPath["startDate"].date() <= self.FlightPath["endDate"]:
                    dateStr = self.FlightPath["startDate"].strftime("%Y-%m-%d")
                    if arrival in self.airportDict["CHECKURL"] or departure in self.airportDict["CHECKURL"]:
                        if arrival in self.airportDict["CHECKURL"] and departure in self.airportDict["CHECKURL"]:
                            url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originMac={departure}&destinationMac={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginMac={departure}&tpDestinationMac={arrival}"
                        elif departure in self.airportDict["CHECKURL"]:
                            url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&discount=0&isReturn=false&promoCode=&originMac={departure}&destinationIata={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginMac={departure}&tpDestinationIata={arrival}"
                        elif arrival in self.airportDict["CHECKURL"]:
                            url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&discount=0&isReturn=false&promoCode=&originMac={departure}&destinationIata={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginMac={departure}&tpDestinationIata={arrival}"
                    else:
                        # there is no ALL search terms in the arrival or destinations 
                        url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originIata={departure}&destinationIata={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata={departure}&tpDestinationIata={arrival}"
                    
                    self.driver.get(url)
                    time.sleep(5)

                    action.ClickButton("Button1")
                    currencySymbol = ""
                    if not action.CheckFlightToday():
                        lists = action.AcquireListOfFlights(driver = self.driver,dateStr = dateStr, departure = departure, arrival = arrival, url = url)
                        listOne.extend(lists["listOne"])
                    self.FlightPath["startDate"] += delta # increment day by 1
                    enddateCopy = self.FlightPath["endDate"].strftime("%Y-%m-%d")


                c = ["departure","Arrival","Date","day", "month", "DepartTime","ArrivalTime",f"cost({lists['Currency']})", "url" ]
            
                if flightInfo == "Connection1":
                    df = pd.DataFrame(listOne, columns = c)
                    df[f"cost({lists['Currency']})"] = df[f"cost({lists['Currency']})"].astype(float)
                if flightInfo == "Connection2":
                    df2 = pd.DataFrame(listOne, columns = c)
                    df2[f"cost({lists['Currency']})"] = df2[f"cost({lists['Currency']})"].astype(float)
                    #df.to_excel(rf"C:\Users\35386\Documents\projects\seleniumRyanair\{departure}_{arrival}_{datetartCopy}_{enddateCopy}_{timeNow}.xlsx", index = False)

        self.FlightPath["startDate"]  =  datetime.datetime.strptime(datetartCopy, "%Y-%m-%d") # reseting the dates back for the second run if needed

        newDF = df.merge(df2, left_on='Date', right_on='Date')
        if newDF.shape[0] == 0:
            print("Nothing to Merge")
            sys.exit()

        ########### Post processing ####################

        columns = [i for i in newDF.columns if "£"  in i]
        newDF["Total(€)"]  = newDF["cost(€)"]

        for pound in columns:
            newDF[f"{pound}_Convert"] =  newDF[pound].apply(lambda x: currConvert.convert(x, 'GBP', 'EUR', ForexFileData['date_to_use']))
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

        newDF = newDF[newDF["suits"] == True]
        
        # Full set of columns
        # newDF = newDF["departure_x",
        #             "Arrival_x",
        #             "Date",
        #             "day_x"	,
        #             "month_x",
        #             "DepartTime_x",
        #             "ArrivalTime_x",
        #             "cost(€)",
        #             "url_x",
        #             "departure_y",
        #             "Arrival_y",
        #             "day_y",
        #             "month_y",
        #             "DepartTime_y",
        #             "ArrivalTime_y",
        #             "cost(£)",
        #             "url_y",
        #             "Total(€)",
        #             "cost(£)_Convert",
        #             "datetimeDepartX",
        #             "datetimeArriveX",
        #             "datetimeDepartY",
        #             "datetimeArriveY",
        #             "suits",
        #             "layovertime",
        #             "TotalTravelTime"]


        # Trimmed Columns
        newDF = newDF[["departure_x",
                    "Arrival_x",
                    "Date",
                    "day_x",
                    "month_x",
                    "DepartTime_x",
                    "ArrivalTime_x",
                    "departure_y",
                    "Arrival_y",
                    "DepartTime_y",
                    "ArrivalTime_y",
                    "Total(€)",
                    "layovertime",
                    "TotalTravelTime",
                    "url_x",
                    "url_y"]]

        ################################# END POSTPROCESSING ##############################

        #newDF = action.DirectFlightDF("Knock", "Milan Bergamo", newDF)
        

        newDF.to_excel(rf"C:\Users\35386\Documents\projects\seleniumRyanair\{self.FlightPath['From']}_TO_{self.FlightPath['To']}_{datetartCopy}_{enddateCopy}_{timeNow}.xlsx", index  = False)

        self.driver.close()



    def DataMerger(self):
        pass

FlightDataCreator().FLightFinder()

    # %%
