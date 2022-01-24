# #%%
# from time import strptime
# import pandas as pd
# import datetime 
# import numpy as np
# import urllib.request
# from datetime import date, timedelta
# from currency_converter import ECB_URL, CurrencyConverter
# import os.path as op
# import os


# def DownloadForexFile():
#     ForexFolder = r"C:\Users\35386\Documents\projects\seleniumRyanair\ForexLoads"
#     ForexFolderContents  = [name for name in os.listdir(ForexFolder)]
#     todaysFileName = f"ecb_{date.today():%Y%m%d}.zip"
#     if len(ForexFolderContents) > 0:
#         for i in ForexFolderContents:
#             if i != todaysFileName:
#                 os.remove(os.path.join(ForexFolder, i ))
    
#     filename = os.path.join(ForexFolder,  f"ecb_{date.today():%Y%m%d}.zip")
    
#     if not op.isfile(filename):
#         urllib.request.urlretrieve(ECB_URL, filename)
#     return filename

# c = CurrencyConverter(DownloadForexFile(), fallback_on_missing_rate=True)

# # Load your custom file
# newDF =pd.read_excel(r"C:\Users\35386\Documents\projects\seleniumRyanair\STN_AOI_2022-02-11_2022-10-31_2022-01-20180134.xlsx")
# columns = [i for i in newDF.columns if "£"  in i]
# newDF["Total(€)"]  = newDF["cost(€)"]
# for pound in columns:
#     newDF[f"{pound}_Convert"] =  newDF[pound].apply(lambda x: c.convert(x, 'GBP', 'EUR', date=date.today() - timedelta(days = 1)))
#     newDF["Total(€)"] = newDF["Total(€)"] + newDF[f"{pound}_Convert"]


# #newDF["Suits"] ="1" if datetime.datetime.strptime(newDF["ArrivalTime_x"],"%H:%M")  <= datetime.datetime.strptime(newDF["DepartTime_y"],"%H:%M") else "0"
# newDF["datetimeDepartX"]= [datetime.datetime.strptime(i, "%H:%M") for i in newDF["DepartTime_x"] ]
# newDF["datetimeArriveX"] = [datetime.datetime.strptime(i, "%H:%M") for i in newDF["ArrivalTime_x"] ]

# newDF["datetimeDepartY"]= [datetime.datetime.strptime(i, "%H:%M") for i in newDF["DepartTime_y"] ]
# newDF["datetimeArriveY"] = [datetime.datetime.strptime(i, "%H:%M") for i in newDF["ArrivalTime_y"] ]


# newDF['suits'] = np.where(newDF["datetimeArriveX"]  <=  newDF["datetimeDepartY"] , True, False)
# newDF['layovertime'] =  np.where(newDF["suits"] == True, newDF["datetimeDepartY"] - newDF["datetimeArriveX"], False  ) 
# newDF["TotalTravelTime"] =  np.where(newDF["suits"] == True, newDF["datetimeArriveY"] - newDF["datetimeDepartX"] , False  ) 
# newDF["Total(€)"] = newDF["Total(€)"].apply(lambda x: round(x,2))


# newDF[["Total(€)", "cost(€)", "cost(£)", f"{pound}_Convert"]].head()

# %%

import itertools 
depart1 = ["Knock", "Dublin", "Shannon"]
arrival1 = ["LdnStn"]

depart2 = arrival1
arrival2 = ["Ancona"]

#list1_permutations1 = all_combinations = [list(zip(each_permutation, depart1)) for each_permutation in itertools.permutations(depart1, len(arrival1))]



list1_permutations2 = all_combinations = [list(zip(each_permutation, depart2)) for each_permutation in itertools.permutations(depart2, len(arrival2))]

list1_permutations2

