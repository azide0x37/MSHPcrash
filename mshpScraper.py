"""
mshpScraper.py 
Missouri State Highway Patrol scraper for crash data!
[azide0x37] Alexander Templeton (nepenthe.me)

Returns: pandas Data.Frame object

Class usage template
myScrape = mshpScraper()
myScrape()
"""

import urllib2
import sklearn.preprocessing, sklearn.decomposition, sklearn.linear_model, sklearn.pipeline, sklearn.metrics

import pandas as pd
import numpy as np

from bs4 import BeautifulSoup
from datetime import datetime
from collections import OrderedDict
from sklearn_pandas import DataFrameMapper, cross_val_score


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
            counter = 1

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
        returnData = pd.DataFrame(dataset)
        returnData = returnData.drop(['Name', 'Hometown', 'Date', 'Time', 'Location'], axis=1)
        
        #Ship it!
        return returnData

myScrape = mshpScraper()
data = myScrape()
mapper = DataFrameMapper([
    ('Age', sklearn.preprocessing.OneHotEncoder()),
    ('Severity', sklearn.preprocessing.LabelBinarizer()),
    ('County', sklearn.preprocessing.LabelBinarizer()),
    ('Troop', sklearn.preprocessing.LabelBinarizer())
    ])
    
print np.round(mapper.fit_transform(data), 2)
