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
import geopy
import pandas as pd
import numpy as np
import sklearn.preprocessing, sklearn.decomposition, sklearn.linear_model, sklearn.pipeline, sklearn.metrics
from sklearn_pandas import DataFrameMapper, cross_val_score
from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime

class mshpScraper:
    
    def __init__(
                self,
                url = 'http://www.mshp.dps.missouri.gov/HP68/SearchAction', 
                colNames = ['Name', 'Age', 'Hometown', 'Severity', 'Date', 'Time', 'County', 'Location', 'Troop'], 
                county = 'Jefferson'):

        self.url = url
        self.colNames = colNames
        
        #Use a proper useragent to evade the anti-hack software
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        
        #Cache our response
        self.response = opener.open(self.url)
    
        #Set better formatting for testing console print
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 200)
    
    def __str__(self):
        try:
            return self.url
        except:
            print "Unable to print url." 
    
    #Setting this default method allows one to call an instance like a function. NEATO!
    def __call__(self, refreshCache = False):
        
        if refreshCache:
            self.__init__()
        
        webpageSouped = BeautifulSoup(self.response.read())

        #This is the particular table with the data we need.
        #TODO: Find a better way to pick the right one?
        table = webpageSouped.find('table', summary="Table listing details of the accident.")
        rows = table.findAll('tr')
        
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

        #Convert dataset (List of Dicts) to pandas DataFrame
        #Extract date and time colums to column of dateTime objects, then drop
        
        def datetimeCoerce(row):
            return datetime(row['Date'], axis = 1)


        returnData = pd.DataFrame(dataset)
        #returnData['DateTime'] = returnData.apply(lambda row: datetimeCoerce(row))
        
        #FIXME drop these unused columns
        #returnData.drop('Date', 1, inplace = True)

        #FIXME this doesn't work at all
        
        #Location coersion
        #geolocator = geopy.geocoders.OpenMapQuest()

        #location = geolocator.geocode(returnData['Location'])
        
        #returnData['Location'] = returnData.apply(lambda row: geolocator.geocode(row.Location + ", " + row.County + " County, MO"))
        #returnData['Latitude'] = returnData.apply(lambda row: geolocator.geocode(row['Location']).latitude)
        #returnData['Longitude'] = returnData.apply(lambda row: geolocator.geocode(row['Location']).longitude)
        
        returnData = returnData.drop('Name', axis=1)
        returnData = returnData.drop('Hometown', axis=1)
        returnData = returnData.drop('Date', axis=1)
        returnData = returnData.drop('Time', axis=1)
        returnData = returnData.drop('Location', axis=1)
        #Ship it!
        print returnData
        return returnData

myScrape = mshpScraper()
data = myScrape()
mapper = DataFrameMapper([
    ('Age', sklearn.preprocessing.StandardScaler()),
    ('Severity', sklearn.preprocessing.LabelBinarizer()),
    ('County', sklearn.preprocessing.LabelBinarizer()),
    ('Troop', sklearn.preprocessing.LabelBinarizer())
    ])
    
print np.round(mapper.fit_transform(data), 2)
pipe = sklearn.pipeline.Pipeline([
    ('featurize', mapper),
    ('lm', sklearn.linear_model.LinearRegression())
    ])
print np.round(cross_val_score(pipe, data, [34, 'Jefferson', 'Fatal', 'C'], 'r2'), 2)
