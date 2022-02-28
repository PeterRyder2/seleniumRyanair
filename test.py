#%%
from locale import currency
from selenium import webdriver
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import re
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
from selenium.common.exceptions import NoSuchElementException        


class Actions:
    def __init__(self, driver, XpathDict, airportdf = None,FligthPath = None, airportList = None):
        self.XpathDict = XpathDict
        self.driver = driver
        self.FlightPath =  FligthPath
        self.delta = datetime.timedelta(days=1)
        self.airportList = airportList
        self.CurrentListDateTimes = None
        self.airportdf =  airportdf

    def ConstructDatetimesFromList(self, flightType = None, url = None):
        FullUL = f"/html/body/flights-root/div/div[1]/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/div/div[2]/div/carousel-container/carousel/div/ul"
        ULText = self.driver.find_element(By.XPATH,FullUL).text.replace("\n", "")
        ULText = ULText.upper()
        # constructDatetimesFromThis

        CurrentListDateTimes = []
        if self.FlightPath[flightType]["startDate"].strftime("%y") == self.FlightPath[flightType]["endDate"].strftime("%y"):
            currency = "€" if "€" in ULText else "£"
            year = self.FlightPath[flightType]["startDate"].strftime("%y")
            #make Datetime
            splits  = ULText.split("DAY")

            splits = [f"{i}day" for i in splits]
            Months =["JAN","FEB","MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


            for date in splits:
                for month in Months:
                    if month in date:
                        pattern =  f"\d\d{month}"
                        v = re.search(pattern, date)
                        if v != None:
                            newString = f"{v.string[v.regs[0][0]:v.regs[0][1]]}{year}"
                            CurrentListDateTimes.append(datetime.datetime.strptime(newString, "%d%b%y").date())
                            print(newString)
                            break
        
        self.CurrentListDateTimes = CurrentListDateTimes

        self.CurrentListDateTimesDict = {}

        v = re.search("\d\d\d\d-\d\d-\d\d", url)
        for count, i in enumerate(CurrentListDateTimes):
            newDate = f"{v.string[v.regs[0][0]:v.regs[0][1]]}"
            self.CurrentListDateTimesDict[count] = [i, i.strftime("%Y-%m-%d"), url.replace(newDate, i.strftime("%Y-%m-%d")) ]


        self.CurrentListDateTimes = self.CurrentListDateTimesDict
      
        return( self.CurrentListDateTimes)

    def CheckUnlistValidaty(self , flightType= None):

        '''
        Returns false if the endate has been reached
        '''
        if self.CurrentListDateTimes[2][0] > self.FlightPath[flightType]["endDate"]:
            
            return False
        else: return True
    def check_exists_by_xpath(self,xpath):

        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True

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
        if "List4Button" ==  xpathKey:
            for xpath in self.XpathDict[xpathKey]:
                if self.check_exists_by_xpath(xpath):
                    self.driver.find_element(By.XPATH,xpath).click()
                    return True
        else: 
            if self.check_exists_by_xpath(self.XpathDict[xpathKey]):
                self.driver.find_element(By.XPATH,self.XpathDict[xpathKey]).click()
                return True
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

        totalList  =list(self.airportdf["IATA"].values) + \
                    list(self.airportdf["Airport"].values) + \
                    list(self.airportdf["RyanairTitle"].values)
        if i in totalList:
            return i
        else: return None


    def  AcquireListOfFlights(self,flightType= None, driver = None ,dateStr = None, departure = None, arrival = None, url = None):
        listOne = []
        DepartString, ArriveString, Departtime, ArrivalTime, price  = (None,)*5

        time.sleep(5)
        str1 =   driver.find_element(By.XPATH,self.XpathDict["FlightList"]).text
      
        str2 = driver.find_element(By.XPATH,"/html/body/flights-root/div/div/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/flight-list/div").text

        str1 = str1.split("Select")

        if "" in str1:
                str1.remove("")
        dateObj = datetime.datetime.strptime(dateStr, "%Y-%m-%d")
        day =  day = calendar.day_name[dateObj.weekday()] 
        month = dateObj.strftime("%b")
     
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


            listOne.append([DepartString,ArriveString,dateStr,day,month,  Departtime,ArrivalTime,price, flightType , url])
            DepartString, ArriveString,Departtime,ArrivalTime,price = (None,)*5 # reassign values to None
            #arrivalTime =splits[1]

        return {"listOne":listOne, "Currency": Currency}
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
##############################################################################################################################################################################################################################################################################################################################################################################
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################
##########################################################################################################################


class FlightDataCreator():

    def __init__(self, airportdf = None , flighDetails =None) -> None:
        self.currentDF  = None
        self.airportdf = airportdf
        self.flightDetails = flighDetails


        self.XPathsDict = {
            "Button1": '//*[@id="cookie-popup-with-overlay"]/div/div[3]/button[2]', # first button to verify cookies
            "FlightList": "/html/body/flights-root/div/div/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/flight-list/div",
            
            "List1": '/html/body/flights-root/div/div[1]/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/div/div[2]/div/carousel-container/carousel/div/ul',
            "List4Button": [ "/html/body/flights-root/div/div[1]/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/div/div[2]/div/carousel-container/carousel/div/ul/li[4]",
                            "/html/body/flights-root/div/div/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/div/div[2]/div/carousel-container/carousel/div/ul/li[4]"],
            "SorryNoFilightAvailable": "/html/body/flights-root/div/div/div/div/flights-lazy-content/flights-summary-container/flights-summary/div/div[1]/journey-container/journey/flight-list/p",
            "ErrorButton": '//*[@id="ry-modal-portal"]/div/trip-error-handling-modal/div/div[2]/button'
        }
        self.startDate = startDate or datetime.date(2022, 3, 1 ) 
        self.endDate = endDate or datetime.date(2022, 3, 4)
        
        # Dates Here
        #startDate = datetime.date.today()
        self.strOneWayStartCopy = self.flightDetails["OneWay"]["startDate"].strftime("%Y-%m-%d")
        self.strOneWayStartEndCopy = self.flightDetails["OneWay"]["endDate"].strftime("%Y-%m-%d")
        self.strReturnEndCopy =self.flightDetails["return"]["startDate"].strftime("%Y-%m-%d")
        self.strReturnEndCopy =self.flightDetails["return"]["endDate"].strftime("%Y-%m-%d")
        self.timeNow = datetime.datetime.now().strftime("%Y-%m-%d%H%m%S")
        self.options = Options()

        self.options.add_argument("--start-maximized")
        #self.options.add_argument('--headless')



        self.driver = webdriver.Chrome(chrome_options=self.options)
        self.action = Actions(self.driver, self.XPathsDict, airportdf = self.airportdf,FligthPath = self.flightDetails)
        self.ForexFileData = self.action.DownloadForexFile()
        self.currConvert = CurrencyConverter(self.ForexFileData['filename'], fallback_on_missing_rate=True)


    def CheckIfAirportIsAll(self,df2, airport):
        ''''
        Checks if the airport is part of a city e.g. Milan , London rather than an airport
        '''
        try:
                
            for row in df2.iterrows():
                if row[1]["IATA"] == airport and row[1]["CheckAll"] == 1:
                    
                    return True
        except Exception as err:
            print(err)
            return False


    def GetUrl(self, flightType  = None, connection = None, flightInfo = None):
        departure = self.flightDetails[flightType][connection]['departure']
        arrival = self.flightDetails[flightType][connection]['arrival']
        dateStr = self.strOneWayStartCopy
        url = None

        if self.CheckIfAirportIsAll(self.airportdf, departure) or self.CheckIfAirportIsAll(self.airportdf, arrival):
            if self.CheckIfAirportIsAll(self.airportdf, departure) and self.CheckIfAirportIsAll(self.airportdf, arrival):
                url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originMac={departure}&destinationMac={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginMac={departure}&tpDestinationMac={arrival}"
            elif self.CheckIfAirportIsAll(self.airportdf, departure):
                url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&discount=0&isReturn=false&promoCode=&originMac={departure}&destinationIata={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginMac={departure}&tpDestinationIata={arrival}"
            elif self.CheckIfAirportIsAll(self.airportdf, arrival):
                url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&discount=0&isReturn=false&promoCode=&originMac={departure}&destinationIata={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginMac={departure}&tpDestinationIata={arrival}"
        else:
            # there is no ALL search terms in the arrival or destinations 
            url = f"https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={dateStr}&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originIata={departure}&destinationIata={arrival}&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={dateStr}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata={departure}&tpDestinationIata={arrival}"
        
        return url

    def GetFlights(self,  returnFlight = False):
        pass

    def MergeDf(self, flightType = None):

        newDF = df.merge(df2, left_on='Date', right_on='Date')

    def MergeConnections(self, flightType = None, lists = None):
        
        if  isinstance(self.flightDetails[flightType]["Connection1"]["df"],pd.DataFrame ) and \
            isinstance(self.flightDetails[flightType]["Connection2"]["df"],pd.DataFrame ) and \
            self.flightDetails[flightType]["MergeConnectDF"] == None:
            
            self.flightDetails[flightType]["MergeConnectDF"] = pd.DataFrame()

            self.flightDetails[flightType]["MergeConnectDF"] = self.flightDetails[flightType]["Connection1"]["df"].merge(self.flightDetails[flightType]["Connection2"]["df"], left_on='Date', right_on='Date')
            #self.flightDetails[flightType]["MergeConnectDF"][f"cost({lists['Currency']})"] = self.flightDetails[flightType]["MergeConnectDF"][f"cost({lists['Currency']})"].astype(float)

            if self.flightDetails[flightType]["MergeConnectDF"].empty:
                print("Nothing to Merge")
                return False
        
        return True

        

    def PostProcessDFs(self, flightType = None):
        newDF = self.flightDetails[flightType]["MergeConnectDF"]
        
        ########### Post processing ####################

        columns = [i for i in newDF.columns if "£"  in i]
        columnsFull = newDF.columns
        if "cost(€)_x" in columnsFull and "cost(€)_y" in columnsFull:
            newDF["Total(€)"]  = newDF["cost(€)_x"] + newDF["cost(€)_y"]
        elif len(columns) > 0:
            for pound in columns:
                newDF[f"{pound}_Convert"] =  newDF[pound].apply(lambda x: self.currConvert.convert(x, 'GBP', 'EUR', self.ForexFileData['date_to_use']))
                newDF["Total(€)"] = newDF["cost(€)"] + newDF[f"{pound}_Convert"]



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

        # Trimmed Columns
        newDF = newDF[["departure_x",
                    "Arrival_x",
                    "flightType_x",
                    "Date",
                    "day_x",
                    "month_x",
                    "DepartTime_x",
                    "ArrivalTime_x",
                    "flightType_y",
                    "Date",
                    "departure_y",
                    "Arrival_y",
                    "DepartTime_y",
                    "ArrivalTime_y",
                    "Total(€)",
                    "layovertime",
                    "TotalTravelTime",
                    "url_x",
                    "url_y"]]

        self.flightDetails[flightType]["MergeConnectDF"] = newDF


    def FLightFinder(self):


        delta = datetime.timedelta(days=1)

        dfList = []
        listOne = []
        flightChoice = ["OneWay"]

        for flightType in flightChoice:
            
            connection = [i for i in self.flightDetails[flightType].keys() if "Connection" in i]
            for connections in connection:
                listOne = []
                departure = self.flightDetails[flightType][connections]['departure']
                arrival = self.flightDetails[flightType][connections]['arrival']
                dateStr = self.strOneWayStartCopy


                url = self.GetUrl(flightType = flightType, connection = connections,  flightInfo =self.flightDetails[flightType])
                print("here")

                        
                self.driver.get(url)
                time.sleep(5)

                self.action.ClickButton("Button1")
                self.action.ClickButton("ErrorButton")


                # Get the Unordered List
                DatetimeURLList = self.action.ConstructDatetimesFromList(flightType= flightType, url = url  )
                while self.action.CheckUnlistValidaty(flightType= flightType): # checks that the current data does not match enddate

                
            
                    if not self.action.CheckFlightToday():
                        lists = self.action.AcquireListOfFlights(driver = self.driver,flightType= flightType, dateStr = DatetimeURLList[2][1], departure = departure, arrival = arrival, url =  DatetimeURLList[2][2])

                        listOne.extend(lists["listOne"])
                    self.action.ClickButton("List4Button")
                    DatetimeURLList  =self.action.ConstructDatetimesFromList(flightType= flightType, url = url ) # get the new list


                    c = ["departure","Arrival","Date","day", "month", "DepartTime","ArrivalTime",f"cost({lists['Currency']})", "flightType", "url" ]
            

                    self.flightDetails[flightType][connections]["df"] = pd.DataFrame(listOne, columns = c)
                    self.flightDetails[flightType][connections]["df"][f"cost({lists['Currency']})"] =  self.flightDetails[flightType][connections]["df"][f"cost({lists['Currency']})"].astype(float)
                    #df.to_excel(rf"C:\Users\35386\Documents\projects\seleniumRyanair\{departure}_{arrival}_{datetartCopy}_{enddateCopy}_{timeNow}.xlsx", index = False)
            self.MergeConnections(flightType=flightType, lists = lists)

            self.PostProcessDFs(flightType=flightType)



        departure = self.flightDetails[flightType]["Connection1"]["departure"]
        arrival  = self.flightDetails[flightType]["Connection2"]["arrival"]

        self.flightDetails[flightType]["MergeConnectDF"].to_excel(rf"C:\Users\35386\Documents\projects\seleniumRyanair\{departure}_TO_{arrival}_{self.strOneWayStartCopy}_{self.strOneWayStartEndCopy}_{self.timeNow}.xlsx", index  = False)

        self.driver.close()
        

        return self.flightDetails[flightType]["MergeConnectDF"]



    def DataMerger(self):
        pass






def Getairports(df2, airport):
    try:
            
        for row in df2.iterrows():
            print(row[1]["Airport"])
            if row[1]["Airport"] == airport:
                
                return row[1]["IATA"]
    except Exception as err:
        print(err)
        return False
        


    

# PARAMETERS #
addreturn = True

startDest = "MilanAll"
connection = "LondonAll"
destination = "Ireland West Airport Knock" 
startDate =  datetime.date(2022, 3, 4 ) 
endDate = datetime.date(2022, 3, 5)
returnStartDate =datetime.date(2022, 4, 1 ) 
returnEndDate = datetime.date(2022, 4, 4)
#"Ireland West Airport Knock"


path= r"C:\Users\35386\Documents\projects\seleniumRyanair\Airports\airports.csv"
airportdf =  pd.read_csv(path)
flighdetails = {
                "addReturn": addreturn,
                "OneWay": {
                    "startDate": startDate ,
                    "endDate": endDate,

                    "Connection1": {"departure":Getairports(airportdf,startDest),
                                    "arrival": Getairports(airportdf,connection),
                                    "df": None},

                    "Connection2": {"departure":Getairports(airportdf, connection),
                                    "arrival": Getairports(airportdf,destination),
                                    "df": None},

                    "MergeConnectDF" : None
                        
                        },
                
                "return": {
                    "startDate": returnStartDate ,
                    "endDate": returnEndDate,

                    "Connection1": {"departure":Getairports(airportdf,destination),
                                    "arrival": Getairports(airportdf,connection),
                                    "df": None},

                    "Connection2": {"departure":Getairports(airportdf, connection),
                                    "arrival": Getairports(airportdf,startDest),
                                    "df": None},

                    "MergeConnectionDF" : None
                        },
}






df = FlightDataCreator(airportdf = airportdf, flighDetails= flighdetails).FLightFinder()
print("done")
    # %%
