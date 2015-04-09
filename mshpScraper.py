"""
#mshpScraper.py 
#Missouri State Highway Patrol scraper for crash data!
#[azide0x37] Alexander Templeton (nepenthe.me)
"""
import requests
import datetime
from dateutil import parser
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
        _dataset['Datetime'] = [datetime.datetime.combine(parser.parse(_dataset['Date'][row]).date(), parser.parse(_dataset['Time'][row]).time()) for row in range(len(_dataset['Date']))]        
        #Formatted test print
        #print [datetime.datetime.strftime(_dataset['Datetime'][i], "%c") for i in range(len(_dataset['Date']))]
        #Ship it!
        return _dataset
