import datetime
import re
time1 = "27FebSunday€104.4928FebMonday€27.4901MarTuesday€4.9902MarWednesday€4.9903MarThursday€9.99"
flightPath = {'Connection1': {'departure': 'MIL', 'arrival': 'LON'}, 'Connection2': {'departure': 'LON', 'arrival': 'NOC'}, 'startDate': datetime.datetime(2022, 3, 1, 0, 0), 'endDate': datetime.date(2022, 3, 4), 'From': 'MIL', 'To': 'NOC'}
CurrentListDateTimes = []



if flightPath["startDate"].strftime("%y") == flightPath["endDate"].strftime("%y"):
    currency = "€" if "€" in time1 else "£"
    year = flightPath["startDate"].strftime("%y")
    #make Datetimes

    splits  = time1.split(currency)
    print("here")


    
    for j in splits:
        list1 = [i for i in j]

        for  count, i in enumerate(list1):
            if i.isdigit() or i == ".": continue
            else:
                
                newString = f"{''.join(list1[count-2:count+3])}{year}"
                CurrentListDateTimes.append(datetime.datetime.strptime(newString, "%d%b%y"))
                print(i)
                break
print(CurrentListDateTimes)