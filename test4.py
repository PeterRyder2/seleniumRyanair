import re

url = 'https://www.ryanair.com/ie/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut=2022-03-01&dateIn=&isConnectedFlight=false&isReturn=false&discount=0&promoCode=&originMac=MIL&destinationMac=LON&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate=2022-03-01&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginMac=MIL&tpDestinationMac=LON'

v = re.search("\d\d\d\d-\d\d-\d\d", url)


if v != None:
    newString = f"{v.string[v.regs[0][0]:v.regs[0][1]]}"
print(url)
