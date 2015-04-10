"""
#mshpScraper.py 
#Missouri State Highway Patrol scraper for crash data!
#[azide0x37] Alexander Templeton (nepenthe.me)
"""
import requests
import datetime as dt
import json
from dateutil import parser as psr

from time import sleep
from bs4 import BeautifulSoup
from collections import OrderedDict 
import numpy as np

class mshpScraper:
    
    def __init__(
                self,
                url = 'http://www.mshp.dps.missouri.gov/HP68/SearchAction', 
                colNames = ['Name', 'Age', 'Hometown', 'Severity', 'Date', 'Time', 'County', 'Location', 'Troop'], 
                county = 'Jefferson'):

        self._url = url
        self._colNames = colNames
        
        #Cache our response
        self._response = requests.get(self._url, headers = {'User-Agent': 'Mozilla/5.0'})

    def __str__(self):
        try:
            return self.url
        except:
            print "Unable to print url." 
    
    def __call__(self, refreshCache = False):
        
        if refreshCache:
            self.__init__()
        
        _souped = BeautifulSoup(self._response.text)

        #This is the particular table with the data we need.
        #TODO: Find a better way to pick the right one?
        _table = _souped.find('table', summary="Table listing details of the accident.")
        rows = _table.findAll('tr')
 
        _dataset = OrderedDict((self._colNames[i], []) for i in range(len(self._colNames)))
        
        for tr in rows[1:]:
            cols = tr.findAll('td')
            counter = 0
            for td in cols[1:]:
                try:
                    text = ''.join(td.find(text=True))
                    _dataset[self._colNames[counter]].append(text)
                    counter += 1
                except:
                    counter = 0
        
        #Attempt to coerce date and time to datetime and remove originals
        _dataset['Datetime'] = [dt.datetime.combine(psr.parse(_dataset['Date'][row]).date(), psr.parse(_dataset['Time'][row]).time()) for row in range(len(_dataset['Date']))]        
        #Formatted test print
        #print [datetime.datetime.strftime(_dataset['Datetime'][i], "%c") for i in range(len(_dataset['Date']))]
        
        #Attempt to determine coordinates from approximate address
        #TODO: Is this data manipulation useful?
        response = requests.get("https://michele-zonca-google-geocoding.p.mashape.com/geocode/json?address=MO-6+AND+ROUTE+F+AT+JAMESPORT&sensor=true",
                               headers={"X-Mashape-Key": "143jwvHjaFmshwlsIWWgs21EMbOFp1meDr6jsnmRPcrUFcpfap", "Accept": "application/json"})
        print "Latitude:", response.json()['results'][0]['geometry']['location']['lat'], "Longitude:", response.json()['results'][0]['geometry']['location']['lng']
        #print _dataset['Location']
        latitudes = []        
        totalAddresses = 0
        parsedAddresses = 0
        blank = []
        
        #Merge fuzzy location with county and state data
        _dataset['Location'] = [_dataset['Location'][n] + _dataset['County'][n] + "County, MO" for n in range(len(_dataset['Location']))]
            
        for fuzzyAddress in _dataset['Location']:
            addressResponse = requests.get("https://michele-zonca-google-geocoding.p.mashape.com/geocode/json?address=" + fuzzyAddress.replace(" ","+") + "&sensor=true", headers = {"X-Mashape-Key": "143jwvHjaFmshwlsIWWgs21EMbOFp1meDr6jsnmRPcrUFcpfap", "Accept": "application/json"})
            #print addressResponse.json()['results']#[0]['geometry']['location']['lat']
            #sleep(0.1) 
            totalAddresses += 1
            try:
                blank.append(addressResponse.json()['results'][0]['geometry']['location']['lat'])
                parsedAddresses += 1
            except:
                print addressResponse.json(), "for address", fuzzyAddress
                continue
        print parsedAddresses, "/", totalAddresses, "addresses converted."
        print blank
            
        _dataset['Latitude'] = latitudes
        #print _dataset['Latitude']
        
        
        
        #Ship it!
        return np.array(_dataset)

myScrape = mshpScraper()
data = myScrape()
#print data
