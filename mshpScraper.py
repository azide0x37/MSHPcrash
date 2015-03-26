"""
mshpScraper.py 
Missouri State Highway Patrol scraper for crash data!
[azide0x37] Alexander Templeton (nepenthe.me)
Arguments: 
    Production:
        optional: 
            date:
            name:
            county:
            severity:
            age_of_occupant:
            
    Devel:
        optional: 
            url: of webpage
    
Returns: pandas Data.Frame object

Class usage template
myScrape = mshpScraper()
myScrape()
"""

import urllib2
from bs4 import BeautifulSoup
from collections import OrderedDict
import json
import pandas as pd
from datetime import datetime
from geopy.geocoders import Nominatim

class mshpScraper:
    
    def __init__(
                self,
                url = 'http://www.mshp.dps.missouri.gov/HP68/SearchAction', 
                colNames = ['Name', 'Age', 'Hometown', 'Severity', 'Date', 'Time', 'County', 'Location', 'Troop']), 
                county = 'Jefferson'):
        
        self.url = url
        self.colNames = colNames
        
        #Use a proper useragent to evade the anti-hack software
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        
        #Cache our response
        #TODO: Add __call__ option to redownload 
        self.response = opener.open(self.url)

    
    def __str__(self):
        try:
            return self.url
        except:
            print "Unable to print url." 

    def __call__(self):
        webpageSouped = BeautifulSoup(self.response.read())

        #This is the particular table with the data we need.
        #TODO: Find a better way to pick the right one?
        table = webpageSouped.find('table', summary="Table listing details of the accident.")
        rows = table.findAll('tr')

        #TODO: Pull colNames ftom the table headngs
        dataset = []
        
        for tr in rows:
            cols = tr.findAll('td')
            row_data = OrderedDict()
            counter = 0

            #TODO: the zeroth element of cols is null; why? Fix.
            for td in cols[1:]:
                text = ''.join(td.find(text=True))
                try:
                    row_data[self.colNames[counter]] = text
                    counter += 1
                except:
                    counter = 0
                    continue
            dataset.append(row_data)

        #Convert dataset (List of Dicts) to pandas Dataframe
        #Extract date and time colums to column of dateTime objects, then drop
        returnData = pd.DataFrame(dataset)
        returnData['DateTime'] = returnData.apply(lambda row datetime(row['Date'], row['Time'], axis = 1)
        returnData = returnData.drop(['Date', 'Time'], 1)

        #Location coersion
        geolocator = Nominatim()
        returnData['Location'] = returnData.apply(lambda row geolocator.geocode(row.Location + ", " + row.County + " County, MO"))
        returnData['Latitude'] = returnData.apply(lambda row geolocator.geocode(row['Location']).latitude)
        returnData['Longitude'] = returnData.apply(lambda row geolocator.geocode(row['Location']).longitude)

        #Ship it!
        return returnData
