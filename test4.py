
import datetime
import re
time1 = "27FebSunday€104.4928FebMonday€27.4901MarTuesday€4.9902MarWednesday€4.9903MarThursday€9.99"
flightPath = {'Connection1': {'departure': 'MIL', 'arrival': 'LON'}, 'Connection2': {'departure': 'LON', 'arrival': 'NOC'}, 'startDate': datetime.datetime(2022, 3, 1, 0, 0), 'endDate': datetime.date(2022, 3, 4), 'From': 'MIL', 'To': 'NOC'}
CurrentListDateTimes = []



val = ['03MARTHURS', '€7.9904MARFRI', '05MARSATUR', '€7.9906MARSUN', '€7.9907MARMON', '€7.99']
Months =["JAN","FEB","MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
year = "22"


for date in val:
    for month in Months:
        if month in date:
            pattern =  f"\d\d{month}"
            v = re.search(pattern, date)
            if v != None:
                newString = v.string[v.regs[0][0]:v.regs[0][1]]
                CurrentListDateTimes.append(datetime.datetime.strptime(newString, "%d%b%y").date())
                print(newString)
                break
        
