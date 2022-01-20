
from time import strptime
import pandas as pd
import datetime 
newDF =pd.read_excel(r"C:\Users\35386\Documents\projects\seleniumRyanair\STN_AOI_2022-02-11_2022-02-16_2022-01-20000130.xlsx")
newDF["Total"] = newDF["cost(€)"] + newDF["cost(£)"]

#newDF["Suits"] ="1" if datetime.datetime.strptime(newDF["ArrivalTime_x"],"%H:%M")  <= datetime.datetime.strptime(newDF["DepartTime_y"],"%H:%M") else "0"
# newDF["datetimeArriveX"] = [datetime.datetime.strptime(i, "%H:%M") for i in newDF["ArrivalTime_x"] ]
# newDF["datetimeDepartY"] = [datetime.datetime.strptime(i, "%H:%M") for i in newDF["DepartTime_y"] ]
# newDF["Suits"] = newDF[newDF ["datetimeArriveX"] < newDF["datetimeDepartY"]]


df2 = (newDF, index = newDF["Date"])
print(newDF)

# d1 = "21:11"

# date1 = datetime.datetime.strptime(d1, "%H:%M") 

# d2 = "21:10"

# date2 = datetime.datetime.strptime(d1, "%H:%M") 


# if d1 < d2:
#     print("here")