from requests import get
from urllib.error import URLError, HTTPError
from html import unescape
import json
from dateutil.parser import parse
from dateutil.parser import parserinfo
from datetime import datetime
from pytz import timezone

source_tz = timezone('CET')
output_tz = timezone('Europe/Helsinki')

def palautaDataSarakkeista(jsondata, sarakkeet=(0,)):
    """ Hakee JSON-lähdedatasta haluttujen päivien tiedot.
    Sarake 0 = viimeisin päivä eli joko kuluva tai tuleva päivä. """
    data = []

    for sarake in sarakkeet:
        for row in jsondata["data"]["Rows"]:
            if not (row.get("IsExtraRow", True)) and (row.get("Columns")[sarake].get("Value", "-")) != '-':
                hour = unescape(row.get("Name")).split()[0]
                
                tuntiHinta = row.get("Columns")[sarake].get("Value", None)

                aika = source_tz.localize(
                    parse(row.get("Columns")[sarake].get("CombinedName", None) + "T" + hour,
                          parserinfo(dayfirst=True)))
                
                hinta = float(tuntiHinta.replace(',','.'))
                tunti = {}
                tunti['timestamp'] = aika
                tunti['spotprice'] = hinta

                data.append(tunti)

    return data


def haeDataServerilta():
    #Hakee JSON raakadatan serveriltä ja palauttaa sen dictionaryna

    try:
        response = get("http://www.nordpoolspot.com/api/marketdata/page/35?currency=,,,EUR")
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        return ('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach a server.')
        return ('Reason: ', e.reason)
    else:
        # everything is fine
        return (json.loads(response.text))


def getDayAheadPrices():
    return palautaDataSarakkeista(haeDataServerilta(), (1, 0))


def getCurrentSpotPrice():
    # Palauttaa Suomen tämänhetkisen sähkön hinnan
    currentTime = output_tz.localize(datetime.now())
    currentHour = currentTime.replace(second=0, microsecond=0, minute=0)
    priceData = getDayAheadPrices()

    for price in priceData:
        if currentHour == price['timestamp']:
            return price['spotprice']
    
    return None
